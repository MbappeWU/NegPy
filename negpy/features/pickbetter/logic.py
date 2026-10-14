from dataclasses import replace

from negpy.domain.models import WorkspaceConfig
from negpy.features.exposure.logic import kelvin_to_wb, wb_to_kelvin
from negpy.features.pickbetter.models import PICK_PARAMS, Phase, PickBetterProgress, PickParam, RoundKind


def _clamp(value: float, param: PickParam) -> float:
    """Clamp a candidate to the field's slider range."""
    return max(param.lo, min(param.hi, value))


def param_value(config: WorkspaceConfig, param: PickParam) -> float:
    """Read a control's current value: the field itself, or Kelvin for the compound Temperature."""
    if param.compound:
        return wb_to_kelvin(config.exposure.wb_magenta, config.exposure.wb_yellow)
    return float(getattr(config.exposure, param.field))


def set_param(config: WorkspaceConfig, param: PickParam, value: float) -> WorkspaceConfig:
    """Return a config with the control set to `value`, clamped to its slider range.

    A single-field control writes its field; the compound Temperature moves wb_magenta/
    wb_yellow along the Planckian direction to land on the Kelvin value.
    """
    value = _clamp(value, param)
    if param.compound:
        m2, y2 = kelvin_to_wb(value, config.exposure.wb_magenta, config.exposure.wb_yellow)
        return replace(config, exposure=replace(config.exposure, wb_magenta=m2, wb_yellow=y2))
    return replace(config, exposure=replace(config.exposure, **{param.field: value}))


def step_for(param: PickParam, selections: int) -> float:
    """The step a strong-vs-weak round proposes: bold at the first selection, halved per later
    selection of the same parameter, never below the floor.
    """
    return max(param.strong_step / (2**selections), param.floor)


def start_pick_better(config: WorkspaceConfig) -> PickBetterProgress:
    """The first round: param 0 (grade), strong-vs-weak at its full (bold) step."""
    param = PICK_PARAMS[0]
    return PickBetterProgress(
        phase=Phase.FIXED,
        param_index=0,
        round_kind=RoundKind.STRONG_WEAK,
        center_before=param_value(config, param),
        selection_counts=tuple(0 for _ in PICK_PARAMS),
    )


def current_pair(
    config: WorkspaceConfig,
    progress: PickBetterProgress,
) -> tuple[WorkspaceConfig, WorkspaceConfig]:
    """The two candidates to render, differing in one ExposureConfig field.

    A STRONG_WEAK round is center +/- step (left stronger, right weaker), the step bold at the
    parameter's first selection and smaller on each later one. A CHOSEN_MIDDLE round offers the
    committed value nudged a half step further in the committed direction (left) against the
    pre-tuning value (right), so a pick of either half always moves.
    """
    param = PICK_PARAMS[progress.param_index]
    current = param_value(config, param)
    step = step_for(param, progress.selection_counts[progress.param_index])
    if progress.round_kind == RoundKind.STRONG_WEAK:
        left_val = _clamp(current + step, param)
        right_val = _clamp(current - step, param)
        # At a bound a candidate clamps back onto current, so a pick of it is a no-op that
        # shows only the parameter name. Nudge it onto the open side so a pick always moves.
        if left_val == current:
            left_val = _clamp(current - step / 2, param)
        if right_val == current:
            right_val = _clamp(current + step / 2, param)
    else:
        # The left (committed value) equals the center Skip frame, so a pick of it is a no-op
        # showing only the parameter name. Nudge it a half step in the committed direction; the
        # pre-tuning value on the right always differs from current.
        direction = 1.0 if current > progress.center_before else -1.0
        left_val = _clamp(current + direction * step / 2, param)
        if left_val == current:
            left_val = _clamp(current - direction * step / 2, param)
        right_val = progress.center_before
    left = set_param(config, param, left_val)
    right = set_param(config, param, right_val)
    return left, right


def apply_pick(
    config: WorkspaceConfig,
    progress: PickBetterProgress,
    side: int,
) -> tuple[WorkspaceConfig, PickBetterProgress]:
    """Commit the chosen half (side 0 = left, 1 = right) and advance to the next round.

    A STRONG_WEAK pick counts as one selection of the in-flight parameter, so its next
    opportunity proposes a smaller step; a CHOSEN_MIDDLE pick does not.
    """
    left, right = current_pair(config, progress)
    new_config = left if side == 0 else right
    counts = progress.selection_counts
    if progress.round_kind == RoundKind.STRONG_WEAK:
        i = progress.param_index
        counts = counts[:i] + (counts[i] + 1,) + counts[i + 1 :]
    return new_config, _advance(new_config, progress, counts)


def move_summary(old: WorkspaceConfig, new: WorkspaceConfig, progress: PickBetterProgress) -> str:
    """The "Name +delta" line shown for a few seconds after a left or right pick.

    The delta is the committed value minus the pre-pick value (a clamp shows the actual
    movement); a pick that keeps the value shows the name alone, with no delta.
    """
    param = PICK_PARAMS[progress.param_index]
    delta = param_value(new, param) - param_value(old, param)
    if abs(delta) < 1e-9:
        return param.name
    return f"{param.name} {delta:+g}"


def reject_and_advance(
    config: WorkspaceConfig,
    progress: PickBetterProgress,
) -> tuple[WorkspaceConfig, PickBetterProgress]:
    """Reject both candidates (keep the middle current photo) and advance to the next parameter.

    A reject is not a selection: the config and the selection counts stay put, so the next
    parameter's first round still opens at its bold step. The advance is uniform across the
    fixed and refine phases — both move to the next parameter's STRONG_WEAK round.
    """
    if progress.phase == Phase.FIXED:
        next_index = progress.param_index + 1
        if next_index < len(PICK_PARAMS):
            param = PICK_PARAMS[next_index]
            return config, PickBetterProgress(
                phase=Phase.FIXED,
                param_index=next_index,
                round_kind=RoundKind.STRONG_WEAK,
                center_before=param_value(config, param),
                selection_counts=progress.selection_counts,
            )
        param = PICK_PARAMS[0]
        return config, PickBetterProgress(
            phase=Phase.REFINE,
            param_index=0,
            round_kind=RoundKind.STRONG_WEAK,
            center_before=param_value(config, param),
            selection_counts=progress.selection_counts,
        )
    next_index = (progress.param_index + 1) % len(PICK_PARAMS)
    param = PICK_PARAMS[next_index]
    return config, PickBetterProgress(
        phase=Phase.REFINE,
        param_index=next_index,
        round_kind=RoundKind.STRONG_WEAK,
        center_before=param_value(config, param),
        selection_counts=progress.selection_counts,
    )


def _advance(
    config: WorkspaceConfig,
    progress: PickBetterProgress,
    counts: tuple[int, ...],
) -> PickBetterProgress:
    if progress.phase == Phase.FIXED:
        if progress.round_kind == RoundKind.STRONG_WEAK:
            # Round 1 done; the committed value is now the field's center for round 2.
            return PickBetterProgress(
                phase=Phase.FIXED,
                param_index=progress.param_index,
                round_kind=RoundKind.CHOSEN_MIDDLE,
                center_before=progress.center_before,
                selection_counts=counts,
            )
        next_index = progress.param_index + 1
        if next_index < len(PICK_PARAMS):
            param = PICK_PARAMS[next_index]
            return PickBetterProgress(
                phase=Phase.FIXED,
                param_index=next_index,
                round_kind=RoundKind.STRONG_WEAK,
                center_before=param_value(config, param),
                selection_counts=counts,
            )
        # All eleven params settled; begin the endless refinement at param 0.
        param = PICK_PARAMS[0]
        return PickBetterProgress(
            phase=Phase.REFINE,
            param_index=0,
            round_kind=RoundKind.STRONG_WEAK,
            center_before=param_value(config, param),
            selection_counts=counts,
        )
    return _advance_refine(config, progress, counts)


def _advance_refine(
    config: WorkspaceConfig,
    progress: PickBetterProgress,
    counts: tuple[int, ...],
) -> PickBetterProgress:
    param = PICK_PARAMS[progress.param_index]
    if step_for(param, counts[progress.param_index]) <= param.floor:
        # At the floor: move to the next param, restarting its halving from the bold step.
        next_index = (progress.param_index + 1) % len(PICK_PARAMS)
        next_param = PICK_PARAMS[next_index]
        return PickBetterProgress(
            phase=Phase.REFINE,
            param_index=next_index,
            round_kind=RoundKind.STRONG_WEAK,
            center_before=param_value(config, next_param),
            selection_counts=counts,
        )
    return PickBetterProgress(
        phase=Phase.REFINE,
        param_index=progress.param_index,
        round_kind=RoundKind.STRONG_WEAK,
        center_before=param_value(config, param),
        selection_counts=counts,
    )


def is_finished(progress: PickBetterProgress) -> bool:
    """The refinement is endless; the user ends via the Finish button or the toggle, not here."""
    return False
