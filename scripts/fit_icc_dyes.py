"""Fit a print stock's dye coupling to an RGB input profile read on Adobe RGB.

Dev tool, not shipped. The Digital (Pakon Minilab) stock's `dye_matrix` in
negpy/features/exposure/papers.py reproduces tests/fixtures/RGBScan.icc ("Pakon spac unblended toe
g22", public domain), applied to the Adobe RGB output the way the export applies an input profile:
lcms, 16 bit, relative colorimetric with black point compensation.
The profile keeps neutrals, so the stock keeps Digital's curve and only the coupling is fitted, by
Levenberg–Marquardt on CIEDE2000 over an L*C*h grid inside Adobe RGB, through the print kernel's dye
mix and black point compensation.

Usage:
    uv run python scripts/fit_icc_dyes.py [ICC]
"""

import argparse
import pathlib

import imagecodecs
import numpy as np
from fit_print_dyes import ADOBE_TO_XYZ, W65, coupling, de2000, lab, levenberg_marquardt

from negpy.features.exposure.models import EXPOSURE_CONSTANTS
from negpy.features.exposure.papers import PAPER_PROFILES
from negpy.infrastructure.display.color_spaces import WORKING_COLOR_SPACE, ColorSpaceRegistry

REPO = pathlib.Path(__file__).resolve().parents[1]
GAMMA = 563 / 256
BLACK = 10.0 ** -EXPOSURE_CONSTANTS["d_max"]


def lab_to_adobe(L):
    fy = (L[..., 0] + 16) / 116
    f = np.stack([fy + L[..., 1] / 500, fy, fy - L[..., 2] / 200], -1)
    xyz = np.where(f > 6 / 29, f**3, 3 * (6 / 29) ** 2 * (f - 4 / 29)) * W65
    return xyz @ np.linalg.inv(ADOBE_TO_XYZ).T


def grid():
    """Linear Adobe RGB colors on an L*C*h grid, the ones inside the gamut."""
    L, h, c = np.meshgrid(np.arange(20, 91, 10.0), np.radians(np.arange(0, 360, 15.0)), (5, 10, 20, 30, 45, 60, 80.0))
    rgb = lab_to_adobe(np.stack([L, c * np.cos(h), c * np.sin(h)], -1).reshape(-1, 3))
    return rgb[((rgb >= 0) & (rgb <= 1)).all(1)]


def profile_on_adobe(rgb, icc):
    adobe = pathlib.Path(ColorSpaceRegistry.get_icc_path(WORKING_COLOR_SPACE)).read_bytes()
    enc = np.round(np.clip(rgb, 0, 1) ** (1 / GAMMA) * 65535).astype(np.uint16).reshape(-1, 1, 3)
    out = imagecodecs.cms_transform(enc, icc, adobe, colorspace="RGB", outcolorspace="RGB", intent=1, flags=0x2000)
    return (out.reshape(rgb.shape) / 65535.0) ** GAMMA


def stock(rgb, m):
    """A Digital print of these colors re-mixed by dye coupling m, black point compensated as the kernel does."""
    d = -np.log10(rgb * (1 - BLACK) + BLACK)
    return np.clip((10.0 ** -(d @ m.T) - BLACK) / (1 - BLACK), 0, 1)


def main():
    ap = argparse.ArgumentParser(description="Fit a print stock dye coupling to an RGB input profile.")
    ap.add_argument("icc", nargs="?", type=pathlib.Path, default=REPO / "tests" / "fixtures" / "RGBScan.icc")
    args = ap.parse_args()
    rgb = grid()
    target = lab(profile_on_adobe(rgb, args.icc.read_bytes()) @ ADOBE_TO_XYZ.T)

    def error(m):
        return de2000(lab(stock(rgb, m) @ ADOBE_TO_XYZ.T), target)

    fitted = coupling(levenberg_marquardt(lambda o: error(coupling(o)), np.zeros(6)))
    shipped = np.array(PAPER_PROFILES["pakon"].dye_matrix) if "pakon" in PAPER_PROFILES else None
    print(f"{args.icc.name} on {len(rgb)} grid colors, dE00 mean / p95:")
    for name, m in (("Digital, no coupling", np.eye(3)), ("papers.py pakon", shipped), ("fitted", fitted)):
        if m is not None:
            e = error(m / m.sum(1, keepdims=True))
            print(f"   {name:22s} {e.mean():5.2f} / {np.percentile(e, 95):5.2f}")
    rows = ",\n".join(f"        ({', '.join(f'{v:.4f}' for v in r)})" for r in fitted)
    print(f"   dye_matrix=(\n{rows},\n    ),")


if __name__ == "__main__":
    main()
