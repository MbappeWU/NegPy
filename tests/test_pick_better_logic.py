import pytest
from dataclasses import replace

from negpy.domain.models import WorkspaceConfig
from negpy.features.pickbetter.logic import (
    apply_pick,
    current_pair,
    is_finished,
    move_summary,
    param_value,
    randomize_remaining,
    reject_and_advance,
    set_param,
    start_pick_better,
    step_for,
)
from negpy.features.pickbetter.models import Phase, PICK_PARAMS, PickBetterProgress, RoundKind


def _config(**exposure_fields) -> WorkspaceConfig:
    return replace(WorkspaceConfig(), exposure=replace(WorkspaceConfig().exposure, **exposure_fields))


def _zeros() -> tuple[int, ...]:
    return tuple(0 for _ in PICK_PARAMS)


def _count_at(index: int, value: int) -> tuple[int, ...]:
    counts = [0] * len(PICK_PARAMS)
    counts[index] = value
    return tuple(counts)


class TestStart:
    def test_first_round_is_grade_strong_weak(self):
        progress = start_pick_better(WorkspaceConfig())
        assert progress.phase == Phase.FIXED
        assert progress.param_index == 0
        assert progress.round_kind == RoundKind.STRONG_WEAK
        # First selection of a parameter is bold: the step is its full strong_step.
        assert step_for(PICK_PARAMS[0], progress.selection_counts[0]) == PICK_PARAMS[0].strong_step
        assert progress.center_before == 115.0  # default grade


class TestFixedSequence:
    def test_first_pair_is_center_plus_minus_step(self):
        progress = start_pick_better(WorkspaceConfig())
        left, right = current_pair(WorkspaceConfig(), progress)
        assert left.exposure.grade == 135.0  # 115 + 20
        assert right.exposure.grade == 95.0  # 115 - 20

    def test_strong_weak_advances_to_chosen_middle(self):
        progress = start_pick_better(WorkspaceConfig())
        new_config, next_progress = apply_pick(WorkspaceConfig(), progress, side=0)
        assert new_config.exposure.grade == 135.0  # left committed
        assert next_progress.round_kind == RoundKind.CHOSEN_MIDDLE
        assert next_progress.param_index == 0
        assert next_progress.center_before == 115.0
        # A strong-vs-weak pick counts one selection of the in-flight parameter.
        assert next_progress.selection_counts[0] == 1

    def test_chosen_middle_pair_is_committed_vs_center_before(self):
        # After settling grade to 135, the chosen-vs-middle round nudges the committed value a half step further (140) on the left, and
        # offers the pre-tuning value (center_before, 115) on the right.
        config = _config(grade=135.0)
        progress = PickBetterProgress(Phase.FIXED, 0, RoundKind.CHOSEN_MIDDLE, 115.0, _count_at(0, 1))
        left, right = current_pair(config, progress)
        assert left.exposure.grade == 140.0  # 135 + step/2 (step 10 at the second selection)
        assert right.exposure.grade == 115.0

    def test_chosen_middle_advances_to_next_param(self):
        config = _config(grade=135.0)
        progress = PickBetterProgress(Phase.FIXED, 0, RoundKind.CHOSEN_MIDDLE, 115.0, _count_at(0, 1))
        _, next_progress = apply_pick(config, progress, side=0)
        assert next_progress.param_index == 1  # density
        assert next_progress.round_kind == RoundKind.STRONG_WEAK
        assert step_for(PICK_PARAMS[1], next_progress.selection_counts[1]) == PICK_PARAMS[1].strong_step
        assert next_progress.center_before == 1.0  # default density, unchanged by the grade pick

    def test_full_fixed_sequence_order(self):
        # 22 rounds: each of the 11 params gets a strong-weak then a chosen-middle round, in order.
        config = WorkspaceConfig()
        progress = start_pick_better(config)
        seen = []
        for _ in range(len(PICK_PARAMS) * 2):
            seen.append((progress.param_index, progress.round_kind))
            config, progress = apply_pick(config, progress, side=0)
        expected = []
        for i in range(len(PICK_PARAMS)):
            expected.append((i, RoundKind.STRONG_WEAK))
            expected.append((i, RoundKind.CHOSEN_MIDDLE))
        assert seen == expected
        # The 23rd round opens the endless refinement, back at param 0.
        assert progress.phase == Phase.REFINE
        assert progress.param_index == 0
        assert progress.round_kind == RoundKind.STRONG_WEAK

    def test_chosen_value_carries_forward(self):
        # The chosen-vs-middle left pick nudges grade a half step further (135 -> 140), the next param's baseline.
        config = WorkspaceConfig()
        progress = start_pick_better(config)
        config, progress = apply_pick(config, progress, side=0)  # grade -> 135, chosen-middle
        config, progress = apply_pick(config, progress, side=0)  # grade -> 140, advance to density
        assert config.exposure.grade == 140.0
        assert progress.param_index == 1

    def test_chosen_middle_left_pick_always_moves(self):
        # A chosen-vs-middle A pick must change the value: the committed value (135) equaled the
        # Skip frame, so a plain pick would be a no-op. A left pick nudges a half step further.
        config = WorkspaceConfig()
        progress = start_pick_better(config)
        config, progress = apply_pick(config, progress, side=0)  # STRONG_WEAK -> 135
        chosen_middle = progress  # the in-flight CHOSEN_MIDDLE round
        before = config.exposure.grade
        new_config, _ = apply_pick(config, chosen_middle, side=0)  # CHOSEN_MIDDLE A -> 140
        assert new_config.exposure.grade != before


class TestClamping:
    def test_candidate_clamps_to_hi(self):
        # grade 175 + 20 = 195 clamps to hi 180; 175 - 20 = 155 stays in range.
        config = _config(grade=175.0)
        progress = start_pick_better(config)
        left, right = current_pair(config, progress)
        assert left.exposure.grade == 180.0
        assert right.exposure.grade == 155.0

    def test_candidate_clamps_to_lo(self):
        # highlight_density -0.4 - 0.2 = -0.6 clamps to lo -0.5.
        config = _config(highlight_density=-0.4)
        progress = PickBetterProgress(Phase.FIXED, 4, RoundKind.STRONG_WEAK, -0.4, _zeros())
        left, right = current_pair(config, progress)
        assert left.exposure.highlight_density == -0.2
        assert right.exposure.highlight_density == -0.5

    def test_dye_separation_clamps_to_hi(self):
        # dye_separation 1.45 + 0.1 = 1.55 clamps to hi 1.5; 1.45 - 0.1 = 1.35 stays in range.
        config = _config(dye_separation=1.45)
        progress = PickBetterProgress(Phase.FIXED, 7, RoundKind.STRONG_WEAK, 1.45, _zeros())
        left, right = current_pair(config, progress)
        assert left.exposure.dye_separation == 1.5
        assert right.exposure.dye_separation == pytest.approx(1.35)

    def test_preflash_clamps_to_lo(self):
        # preflash 0.05 - 0.1 = -0.05 clamps to lo 0.0; 0.05 + 0.1 = 0.15 stays in range.
        config = _config(preflash=0.05)
        progress = PickBetterProgress(Phase.FIXED, 6, RoundKind.STRONG_WEAK, 0.05, _zeros())
        left, right = current_pair(config, progress)
        assert left.exposure.preflash == pytest.approx(0.15)
        assert right.exposure.preflash == 0.0

    def test_candidate_at_hi_moves_on_the_open_side(self):
        # grade 180 is at the hi bound: 180 + 20 clamps back onto 180 (a no-op pick), so the
        # left candidate is nudged onto the open side (180 - 10 = 170); the right stays 160.
        config = _config(grade=180.0)
        progress = start_pick_better(config)
        left, right = current_pair(config, progress)
        assert left.exposure.grade == 170.0  # nudged below the hi bound so the pick moves
        assert right.exposure.grade == 160.0
        assert left.exposure.grade != right.exposure.grade

    def test_candidate_at_lo_moves_on_the_open_side(self):
        # grade 50 is at the lo bound: 50 - 20 clamps back onto 50 (a no-op pick), so the
        # right candidate is nudged onto the open side (50 + 10 = 60); the left stays 70.
        config = _config(grade=50.0)
        progress = start_pick_better(config)
        left, right = current_pair(config, progress)
        assert left.exposure.grade == 70.0
        assert right.exposure.grade == 60.0  # nudged above the lo bound so the pick moves
        assert left.exposure.grade != right.exposure.grade


class TestCompoundTemperature:
    # Temperature is a compound control: its value is Kelvin, read and written through the
    # wb_magenta/wb_yellow pair, not an ExposureConfig field of its own.
    def test_param_value_reads_kelvin_from_wb(self):
        # Neutral wb (magenta=0, yellow=0) reads back as the 5500K reference.
        assert param_value(WorkspaceConfig(), PICK_PARAMS[10]) == 5500.0

    def test_set_param_moves_the_wb_pair_to_kelvin(self):
        param = PICK_PARAMS[10]
        config = WorkspaceConfig()
        new_config = set_param(config, param, 6000.0)
        # The wb pair moved off neutral, the read-back lands on the target Kelvin, and the
        # original frozen config is untouched.
        assert new_config.exposure.wb_magenta != 0.0
        assert new_config.exposure.wb_yellow != 0.0
        assert param_value(new_config, param) == pytest.approx(6000.0)
        assert config.exposure.wb_magenta == 0.0
        assert config.exposure.wb_yellow == 0.0

    def test_temperature_clamps_to_kelvin_range(self):
        param = PICK_PARAMS[10]
        config = WorkspaceConfig()
        assert param_value(set_param(config, param, 2000.0), param) == pytest.approx(3000.0)
        assert param_value(set_param(config, param, 20000.0), param) == pytest.approx(12000.0)


class TestStepShrinksWithSelections:
    # A strong-vs-weak step is bold on a parameter's first selection and halves on each later
    # selection of the same parameter, never below the floor.
    def test_grade_step_halves_per_selection(self):
        # grade strong_step 20, floor 1: 20, 10, 5, 2.5, 1.25, then the floor (1.0) holds.
        param = PICK_PARAMS[0]
        assert step_for(param, 0) == 20.0
        assert step_for(param, 1) == 10.0
        assert step_for(param, 2) == 5.0
        assert step_for(param, 3) == 2.5
        assert step_for(param, 4) == 1.25
        assert step_for(param, 5) == 1.0  # 20/32 -> clamped to the floor
        assert step_for(param, 9) == 1.0  # the floor holds for any larger count

    def test_second_density_selection_is_smaller_than_the_first(self):
        # The user's example: after one density selection, the next density proposal is bolder-then-smaller.
        param = PICK_PARAMS[1]  # density
        assert step_for(param, 0) > step_for(param, 1)
        assert step_for(param, 0) == 0.3
        assert step_for(param, 1) == pytest.approx(0.15)


class TestRefinement:
    def test_step_halves_to_floor(self):
        # grade: strong_step 20, floor 1. Each refine pick halves the step; when it reaches the
        # floor the next pick advances to the next param.
        config = WorkspaceConfig()
        progress = PickBetterProgress(Phase.REFINE, 0, RoundKind.STRONG_WEAK, 115.0, _zeros())
        steps = []
        for _ in range(5):
            steps.append(step_for(PICK_PARAMS[0], progress.selection_counts[0]))
            config, progress = apply_pick(config, progress, side=0)
        assert steps == [20.0, 10.0, 5.0, 2.5, 1.25]
        assert progress.param_index == 1  # at the floor, the 6th round moves on

    def test_at_floor_advances_to_next_param(self):
        # At the floor (the step for the current count is the floor), the next pick moves to the
        # next param, restarting its halving from the bold step.
        config = WorkspaceConfig()
        progress = PickBetterProgress(Phase.REFINE, 0, RoundKind.STRONG_WEAK, 115.0, _count_at(0, 5))
        _, next_progress = apply_pick(config, progress, side=0)
        assert next_progress.phase == Phase.REFINE
        assert next_progress.param_index == 1  # density
        assert step_for(PICK_PARAMS[1], next_progress.selection_counts[1]) == PICK_PARAMS[1].strong_step

    def test_density_floor_advances_to_param_two(self):
        config = WorkspaceConfig()
        progress = PickBetterProgress(Phase.REFINE, 1, RoundKind.STRONG_WEAK, 1.0, _count_at(1, 5))
        _, next_progress = apply_pick(config, progress, side=0)
        assert next_progress.param_index == 2  # highlight_grade
        assert next_progress.phase == Phase.REFINE
        assert step_for(PICK_PARAMS[2], next_progress.selection_counts[2]) == PICK_PARAMS[2].strong_step

    def test_toe_step_halves_to_floor(self):
        # toe: strong_step 0.1, floor 0.01. Halving 0.1 -> 0.05 -> 0.025 -> 0.0125, then the step
        # reaches the floor and the next pick advances to the next param.
        config = WorkspaceConfig()
        progress = PickBetterProgress(Phase.REFINE, 9, RoundKind.STRONG_WEAK, 0.0, _zeros())
        steps = []
        for _ in range(4):
            steps.append(step_for(PICK_PARAMS[9], progress.selection_counts[9]))
            config, progress = apply_pick(config, progress, side=0)
        assert steps == [0.1, 0.05, 0.025, 0.0125]
        assert progress.param_index == 10  # temperature


class TestReject:
    # A click on the centre current photo rejects both candidates: the config stays put (the
    # current value is kept), the selection counts do not increment, and the cursor advances to
    # the next parameter's STRONG_WEAK round, uniform across the fixed and refine phases.
    def test_config_unchanged_and_counts_do_not_increment(self):
        # Rejecting the grade strong-vs-weak round keeps the current grade and leaves the count at 0.
        config = _config(grade=135.0)
        progress = PickBetterProgress(Phase.FIXED, 0, RoundKind.STRONG_WEAK, 115.0, _zeros())
        new_config, next_progress = reject_and_advance(config, progress)
        assert new_config.exposure.grade == 135.0
        assert next_progress.selection_counts == _zeros()
        assert next_progress.selection_counts[0] == 0

    def test_fixed_advances_to_next_param_strong_weak(self):
        config = WorkspaceConfig()
        progress = start_pick_better(config)
        _, next_progress = reject_and_advance(config, progress)
        assert next_progress.phase == Phase.FIXED
        assert next_progress.param_index == 1
        assert next_progress.round_kind == RoundKind.STRONG_WEAK
        # The next param opens at its bold step, since the reject added no selection.
        assert step_for(PICK_PARAMS[1], next_progress.selection_counts[1]) == PICK_PARAMS[1].strong_step

    def test_fixed_from_chosen_middle_still_advances_to_next_param(self):
        # A reject mid-way through a parameter (the chosen-vs-middle round) still moves on to the
        # next parameter, skipping the rest of the current one.
        config = _config(grade=135.0)
        progress = PickBetterProgress(Phase.FIXED, 0, RoundKind.CHOSEN_MIDDLE, 115.0, _count_at(0, 1))
        _, next_progress = reject_and_advance(config, progress)
        assert next_progress.param_index == 1
        assert next_progress.round_kind == RoundKind.STRONG_WEAK

    def test_fixed_last_param_enters_refine(self):
        # Rejecting the last fixed param (temperature, index 10) opens the refine at param 0.
        config = WorkspaceConfig()
        progress = PickBetterProgress(Phase.FIXED, 10, RoundKind.STRONG_WEAK, 5500.0, _zeros())
        _, next_progress = reject_and_advance(config, progress)
        assert next_progress.phase == Phase.REFINE
        assert next_progress.param_index == 0
        assert next_progress.round_kind == RoundKind.STRONG_WEAK

    def test_refine_advances_to_next_param_wrapping(self):
        # In the refine, a reject moves to the next parameter; at the last param it wraps to 0.
        config = WorkspaceConfig()
        progress = PickBetterProgress(Phase.REFINE, 9, RoundKind.STRONG_WEAK, 0.0, _zeros())
        _, next_progress = reject_and_advance(config, progress)
        assert next_progress.phase == Phase.REFINE
        assert next_progress.param_index == 10
        progress_last = PickBetterProgress(Phase.REFINE, 10, RoundKind.STRONG_WEAK, 5500.0, _zeros())
        _, wrapped = reject_and_advance(config, progress_last)
        assert wrapped.param_index == 0

    def test_does_not_mutate_inputs(self):
        config = _config(grade=135.0)
        progress = PickBetterProgress(Phase.FIXED, 0, RoundKind.STRONG_WEAK, 115.0, _count_at(0, 2))
        reject_and_advance(config, progress)
        # The frozen config and progress are returned unchanged; only the new progress differs.
        assert config.exposure.grade == 135.0
        assert progress.selection_counts == _count_at(0, 2)


class TestUndo:
    # The controller's Undo restores the pre-pick (config, progress) and re-renders; at the logic
    # level that is current_pair being a pure function of (config, progress) and apply_pick never
    # mutating its frozen inputs, so re-rendering the snapshot reproduces the exact pair.
    def test_undo_reproposes_previous_pair(self):
        config = WorkspaceConfig()
        progress = start_pick_better(config)
        # Render the pair, commit the left (grade 135), then restore the snapshot and re-render.
        left1, right1 = current_pair(config, progress)
        apply_pick(config, progress, side=0)
        left2, right2 = current_pair(config, progress)
        assert left1.exposure.grade == left2.exposure.grade == 135.0
        assert right1.exposure.grade == right2.exposure.grade == 95.0

    def test_apply_pick_does_not_mutate_inputs(self):
        config = _config(grade=135.0)
        progress = PickBetterProgress(Phase.FIXED, 0, RoundKind.STRONG_WEAK, 135.0, _zeros())
        apply_pick(config, progress, side=0)
        # The frozen config and progress are returned unchanged; only the new pair differs.
        assert config.exposure.grade == 135.0
        assert progress.selection_counts == _zeros()


class TestFinished:
    def test_is_finished_is_always_false(self):
        assert is_finished(start_pick_better(WorkspaceConfig())) is False
        assert is_finished(PickBetterProgress(Phase.REFINE, 5, RoundKind.STRONG_WEAK, 0.0, _zeros())) is False


class TestDifferenceScale:
    # The Difference slider multiplies the A/B step; the two candidates stay symmetric about the
    # current (Skip) value, so a larger spread moves them further out without moving the center.
    def test_scale_doubles_the_spread(self):
        # grade 115, bold step 20: at scale 2.0 the step is 40, so A is 155 and B is 75.
        progress = start_pick_better(WorkspaceConfig())
        left, right = current_pair(WorkspaceConfig(), progress, scale=2.0)
        assert left.exposure.grade == 155.0
        assert right.exposure.grade == 75.0

    def test_scale_keeps_the_pair_symmetric_about_current(self):
        # A bigger spread moves both candidates out but the midpoint stays the current value.
        config = _config(grade=115.0)
        progress = start_pick_better(config)
        for scale in (0.5, 1.0, 2.0, 4.0):
            left, right = current_pair(config, progress, scale=scale)
            assert (left.exposure.grade + right.exposure.grade) / 2 == pytest.approx(115.0)

    def test_apply_pick_commits_the_scaled_candidate(self):
        # A left pick at scale 2.0 commits the further-out value (155), not the unit-scale 135.
        config = WorkspaceConfig()
        progress = start_pick_better(config)
        new_config, _ = apply_pick(config, progress, side=0, scale=2.0)
        assert new_config.exposure.grade == 155.0


class TestRandomizeOrder:
    # randomize shuffles param_order once at start; selection_counts stay keyed by the real
    # parameter index, so a shuffle reorders the rounds but each parameter's step still shrinks by
    # its own count.
    def test_default_order_is_identity(self):
        progress = start_pick_better(WorkspaceConfig())
        assert progress.param_order == tuple(range(len(PICK_PARAMS)))

    def test_randomized_order_is_a_permutation(self):
        progress = start_pick_better(WorkspaceConfig(), randomize=True)
        assert len(progress.param_order) == len(PICK_PARAMS)
        assert sorted(progress.param_order) == list(range(len(PICK_PARAMS)))

    def test_shuffled_fixed_run_visits_all_params(self):
        # 22 fixed rounds over a shuffled order still cover every one of the eleven parameters once
        # in a strong-weak round.
        config = WorkspaceConfig()
        progress = start_pick_better(config, randomize=True)
        seen = set()
        for _ in range(len(PICK_PARAMS) * 2):
            if progress.round_kind == RoundKind.STRONG_WEAK:
                seen.add(progress.param_order[progress.param_index])
            config, progress = apply_pick(config, progress, side=0)
        assert seen == set(range(len(PICK_PARAMS)))

    def test_selection_count_tracks_the_real_param(self):
        # After a strong-vs-weak pick at a shuffled position, the count increments on that
        # position's real parameter, not on the position index.
        config = WorkspaceConfig()
        progress = start_pick_better(config, randomize=True)
        real = progress.param_order[progress.param_index]
        _, next_progress = apply_pick(config, progress, side=0)
        assert next_progress.selection_counts[real] == 1
        assert sum(next_progress.selection_counts) == 1


class TestMoveSummary:
    # move_summary renders the "Name +delta" line shown briefly after a left or right pick, reading
    # the in-flight parameter through param_order so a shuffled round still names the right control.
    def test_grade_move_shows_name_and_delta(self):
        # grade 115 -> 135 is a +20 move; the line names the control and its signed delta.
        old = WorkspaceConfig()
        new = _config(grade=135.0)
        progress = start_pick_better(old)
        assert move_summary(old, new, progress) == "Grade +20"

    def test_zero_delta_shows_name_only(self):
        # A pick that keeps the value (delta 0) shows the name alone, with no delta.
        config = _config(grade=135.0)
        progress = start_pick_better(config)
        assert move_summary(config, config, progress) == "Grade"

    def test_names_the_real_param_at_the_position(self):
        # With param_order putting density (index 1) at position 0, the summary reads the real
        # parameter, not the position index (grade, index 0).
        old = WorkspaceConfig()
        new = _config(density=1.3)
        progress = PickBetterProgress(
            Phase.FIXED,
            0,
            RoundKind.STRONG_WEAK,
            1.0,
            _zeros(),
            (1, 0, 2, 3, 4, 5, 6, 7, 8, 9, 10),
        )
        assert move_summary(old, new, progress) == "Density +0.3"


class TestRandomizeRemaining:
    # randomize_remaining reshuffles only the not-yet-visited tail; the in-flight round and the
    # rounds already run keep their place, so a mid-tuning Randomize press reorders the upcoming
    # rounds without disturbing the pick in front of the user.
    def test_keeps_the_in_flight_round(self):
        progress = start_pick_better(WorkspaceConfig())
        new = randomize_remaining(progress)
        assert new.param_index == progress.param_index
        assert new.phase == progress.phase
        assert new.round_kind == progress.round_kind
        assert new.center_before == progress.center_before
        assert new.selection_counts == progress.selection_counts

    def test_leaves_the_visited_head_in_place(self):
        # At param_index 3 the first four entries keep their order; only the tail shuffles.
        progress = PickBetterProgress(Phase.FIXED, 3, RoundKind.STRONG_WEAK, 115.0, _zeros())
        new = randomize_remaining(progress)
        assert new.param_order[:4] == progress.param_order[:4]

    def test_full_order_stays_a_permutation(self):
        progress = start_pick_better(WorkspaceConfig())
        new = randomize_remaining(progress)
        assert sorted(new.param_order) == list(range(len(PICK_PARAMS)))

    def test_randomize_actually_shuffles(self):
        # With a fixed seed the tail is a non-identity permutation, so the call is not a no-op.
        import random as _random

        progress = start_pick_better(WorkspaceConfig())
        _random.seed(0)
        new = randomize_remaining(progress)
        assert new.param_order != progress.param_order
        assert sorted(new.param_order) == list(range(len(PICK_PARAMS)))

    def test_last_param_has_no_tail(self):
        # At the last position there is no tail to shuffle, so the order is unchanged.
        progress = PickBetterProgress(Phase.FIXED, len(PICK_PARAMS) - 1, RoundKind.STRONG_WEAK, 115.0, _zeros())
        new = randomize_remaining(progress)
        assert new.param_order == progress.param_order
