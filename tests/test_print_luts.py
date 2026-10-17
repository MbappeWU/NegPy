import numpy as np
import pytest

from negpy.features.exposure import print_lut
from negpy.features.exposure.logic import apply_characteristic_curve, per_channel_curve_params
from negpy.features.exposure.papers import PaperProfile
from negpy.features.exposure.print_lut import DyeLut, load_print_lut, lut_black_luminance, save_print_lut, tetra_lookup


def _linear_table(n=5):
    g = np.linspace(0.0, 1.0, n, dtype=np.float32)
    c, m, y = np.meshgrid(g, g, g, indexing="ij")
    return np.ascontiguousarray(np.stack([0.2 + 0.5 * c, 0.1 + 0.3 * m + 0.2 * c, 0.9 - 0.4 * y], -1).astype(np.float32))


def test_tetra_exact_at_nodes():
    t, e_max = _linear_table(), np.ones(3, np.float32)
    for idx in [(0, 0, 0), (4, 4, 4), (1, 3, 2)]:
        np.testing.assert_allclose(tetra_lookup(t, e_max, *(np.array(idx) / 4)), t[idx], atol=1e-6)


def test_tetra_exact_for_linear_function():
    t, e_max = _linear_table(), np.full(3, 2.0, np.float32)
    for e in np.random.default_rng(0).uniform(0, 2, (200, 3)):
        u = e / 2
        expected = (0.2 + 0.5 * u[0], 0.1 + 0.3 * u[1] + 0.2 * u[0], 0.9 - 0.4 * u[2])
        np.testing.assert_allclose(tetra_lookup(t, e_max, *e), expected, atol=1e-5)


def test_tetra_clamps_outside_range():
    t, e_max = _linear_table(), np.ones(3, np.float32)
    np.testing.assert_allclose(tetra_lookup(t, e_max, -0.5, 9.0, 0.3), tetra_lookup(t, e_max, 0.0, 1.0, 0.3))


def test_save_load_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(print_lut, "LUT_DIR", tmp_path)
    load_print_lut.cache_clear()
    save_print_lut(tmp_path / "t.npz", _linear_table(), np.ones(3, np.float32), "test")
    lut = load_print_lut("t")
    load_print_lut.cache_clear()
    assert lut.source == "test" and lut.table.flags.c_contiguous
    np.testing.assert_array_equal(lut.table, _linear_table())


def _dye_table(n=9, e_max=3.0):
    g = np.linspace(0.0, e_max, n)
    c, m, y = np.meshgrid(g, g, g, indexing="ij")
    d = np.stack([c + 0.10 * m, m + 0.10 * y + 0.05 * c, y + 0.08 * m], -1)
    return np.ascontiguousarray((10.0**-d).astype(np.float32)), np.full(3, e_max, np.float32)


@pytest.fixture
def lut_paper(tmp_path, monkeypatch):
    table, e_max = _dye_table()
    save_print_lut(tmp_path / "t.npz", table, e_max, "test")
    monkeypatch.setattr(print_lut, "LUT_DIR", tmp_path)
    load_print_lut.cache_clear()
    yield PaperProfile(label="t", print_color=DyeLut("t"))
    load_print_lut.cache_clear()


def _colors():
    rng = np.random.default_rng(1)
    return np.concatenate([np.linspace(0, 1, 32)[:, None].repeat(3, 1), rng.uniform(0, 1, (96, 3))])[None].astype(np.float32)


def _render(paper, img=None, d_min=None, bpc=False, **kw):
    d_min = paper.d_min if d_min is None else d_min
    slopes, pivots, _ = per_channel_curve_params(
        grade=115.0, density=1.0, auto_normalize_contrast=False, strength=0.0, lum_range=1.3, textural_range=None, d_min=d_min, paper=paper
    )
    return apply_characteristic_curve(
        _colors() if img is None else img,
        (pivots[0], slopes[0]),
        (pivots[1], slopes[1]),
        (pivots[2], slopes[2]),
        d_min=d_min,
        paper=paper,
        bpc=bpc,
        **kw,
    )[0]


def _expected(lut_paper, bpc, d_min=None):
    plain = PaperProfile(label="t")
    d0 = plain.d_min if d_min is None else d_min
    dens = -np.log10(np.maximum(_render(plain, d_min=d0), 1e-12))  # bpc off: T = 10^-D
    lut = load_print_lut("t")
    t = np.array([tetra_lookup(lut.table, lut.e_max, *(p - d0)) for p in dens]) * 10.0**-d0
    if bpc:
        yb = lut_black_luminance(lut, (d0,) * 3, (plain.d_max,) * 3)
        t = (t - yb) / (1 - yb)
    return np.clip(t, 0, 1)


@pytest.mark.parametrize("bpc", [False, True])
def test_lut_stock_renders_lut_colors(lut_paper, bpc):
    np.testing.assert_allclose(_render(lut_paper, bpc=bpc), _expected(lut_paper, bpc), atol=1e-4)


def test_lut_stock_bpc_off_keeps_tinted_black(lut_paper):
    black = _render(lut_paper, img=np.ones((1, 1, 3), np.float32))[0]
    assert black.max() < 0.02 and black.max() - black.min() > 1e-4
    np.testing.assert_allclose(black, _expected(lut_paper, False)[31], atol=1e-4)


def test_lut_stock_paper_white_off(lut_paper):
    white = _render(lut_paper, img=np.zeros((1, 1, 3), np.float32), d_min=0.0)[0]
    np.testing.assert_allclose(white, _expected(lut_paper, False, d_min=0.0)[0], atol=1e-4)
    assert white.min() > 0.9


def test_lut_stock_density_out_of_range(lut_paper):
    out = _render(lut_paper, bpc=True, shadow_density=1.0, cmy_offsets=(-2.0, -2.0, -2.0))
    assert np.isfinite(out).all() and out.min() >= 0.0 and out.max() <= 1.0
