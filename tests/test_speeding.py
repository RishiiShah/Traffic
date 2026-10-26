"""Tests for the Vehicle speed-estimation helper.

Only the pure `Vehicle` kinematics are exercised here; no model or video is
loaded, so these run offline without weights.
"""
import pytest

# Importing detectors.Speeding pulls in torch/ultralytics; skip the whole
# module cleanly if the ML stack isn't installed in the current environment.
Vehicle = pytest.importorskip("detectors.Speeding").Vehicle


def test_initial_speed_is_zero():
    v = Vehicle(obj_id=1, initial_pos=(0.0, 0.0), frame_idx=0)
    assert v.speed == 0.0


def test_speed_from_horizontal_movement():
    # Moves 10 px over 10 frames at 20 fps with 0.1 m/px.
    #   distance = 10 px * 0.1 m/px = 1.0 m
    #   time     = 10 frames / 20 fps = 0.5 s
    #   speed    = 1.0 / 0.5 = 2.0 m/s
    v = Vehicle(obj_id=1, initial_pos=(0.0, 0.0), frame_idx=0)
    v.update(new_pos=(10.0, 0.0), frame_idx=10, fps=20, mpp=0.1)
    assert v.speed == pytest.approx(2.0)


def test_diagonal_distance_uses_euclidean():
    # 3-4-5 triangle: moving (3,4) px = 5 px.
    #   distance = 5 px * 1.0 m/px = 5 m over 1 frame at 1 fps = 5 m/s
    v = Vehicle(obj_id=2, initial_pos=(0.0, 0.0), frame_idx=0)
    v.update(new_pos=(3.0, 4.0), frame_idx=1, fps=1, mpp=1.0)
    assert v.speed == pytest.approx(5.0)


def test_no_frame_advance_keeps_previous_speed():
    # frame_delta == 0 should not recompute (and must not divide by zero).
    v = Vehicle(obj_id=3, initial_pos=(0.0, 0.0), frame_idx=5)
    v.update(new_pos=(100.0, 0.0), frame_idx=5, fps=30, mpp=0.1)
    assert v.speed == 0.0
