from dataclasses import dataclass
from enum import StrEnum


class Phase(StrEnum):
    """Which iteration phase the proposal is in."""

    FIXED = "fixed"
    REFINE = "refine"


class RoundKind(StrEnum):
    """The kind of pair a fixed-phase round proposes."""

    STRONG_WEAK = "strong_weak"
    CHOSEN_MIDDLE = "chosen_middle"


@dataclass(frozen=True)
class PickParam:
    """One tunable Exposure control the picker proposes.

    `strong_step` is the bold step a first selection moves; `floor` is the smallest step;
    `lo`/`hi` clamp a candidate to its slider range. `compound` marks a control spanning a
    field pair (Temperature moves wb_magenta/wb_yellow; its "value" is Kelvin).
    """

    field: str
    name: str
    strong_step: float
    floor: float
    lo: float
    hi: float
    compound: bool = False


# The eleven tunable Exposure controls, in proposal order: Contrast (grade) and Exposure
# (density) first, then the split grade and split density trims, then Preflash, Dye
# Separation, Snap, Toe and Temperature. The excluded controls (Luma/Color Clip, Crop,
# Crosstalk, Cast Removal, Hue Trim, Black/White Point) never appear here.
PICK_PARAMS: tuple[PickParam, ...] = (
    PickParam("grade", "Grade", 20.0, 1.0, 50.0, 180.0),
    PickParam("density", "Density", 0.3, 0.01, 0.0, 2.0),
    PickParam("highlight_grade", "Highlights Grade", 15.0, 1.0, -50.0, 50.0),
    PickParam("shadow_grade", "Shadows Grade", 15.0, 1.0, -50.0, 50.0),
    PickParam("highlight_density", "Highlights Density", 0.2, 0.01, -0.5, 0.5),
    PickParam("shadow_density", "Shadows Density", 0.3, 0.02, -0.9, 0.9),
    PickParam("preflash", "Preflash", 0.1, 0.01, 0.0, 1.0),
    PickParam("dye_separation", "Dye Separation", 0.1, 0.01, 0.5, 1.5),
    PickParam("midtone_gamma", "Snap", 0.05, 0.005, -0.5, 0.5),
    PickParam("toe", "Toe", 0.1, 0.01, -1.0, 1.0),
    PickParam("temperature", "Temperature", 500.0, 50.0, 3000.0, 12000.0, compound=True),
)


@dataclass(frozen=True)
class PickBetterProgress:
    """The iteration cursor the controller advances after each pick.

    `selection_counts` holds, per parameter, how many times that parameter has been committed;
    the proposed step shrinks with the count (bold at first, smaller on each later selection of
    the same parameter). `center_before` is the value the in-flight field held when its tuning
    started; it is the "middle" the chosen-vs-middle round compares the committed pick against.
    The refine phase runs STRONG_WEAK rounds only, so `center_before` is carried but unused there.
    """

    phase: Phase
    param_index: int
    round_kind: RoundKind
    center_before: float
    selection_counts: tuple[int, ...]
