"""Tests for OCR plate validation and ROI cropping.

These avoid constructing OCR3 (which needs GROQ_API_KEY and a YOLO model) by
testing the module-level plate patterns and calling crop_to_roi on a lightweight
stand-in, so they run offline without weights or network access.
"""
import re

import pytest

np = pytest.importorskip("numpy")
# detectors.OCR imports torch/ultralytics/groq; skip if unavailable.
_ocr = pytest.importorskip("detectors.OCR")
PLATE_PATTERNS = _ocr.PLATE_PATTERNS
OCR3 = _ocr.OCR3


def _normalize(raw: str) -> str:
    """Mirror the normalization perform_ocr applies before matching."""
    return re.sub(r"[^A-Z0-9]", "", raw.upper())


def _is_valid(raw: str) -> bool:
    candidate = _normalize(raw)
    return bool(candidate) and any(p.fullmatch(candidate) for p in PLATE_PATTERNS)


def test_valid_state_format_plate():
    assert _is_valid("MH12AB1234")
    # tolerant of spaces / lowercase in the raw string
    assert _is_valid("mh 12 ab 1234")


def test_valid_bh_series_format():
    assert _is_valid("22BH1234AA")


def test_invalid_plates_rejected():
    assert not _is_valid("")
    assert not _is_valid("NONE")
    assert not _is_valid("ABC123")          # too short / wrong shape
    assert not _is_valid("MH12AB123")       # only 3 trailing digits
    assert not _is_valid("1234567890")      # all digits


def test_crop_to_roi_clamps_out_of_bounds_box():
    img = np.zeros((100, 200, 3), dtype=np.uint8)
    # Box exceeds the image on every side; crop must stay within bounds.
    roi = OCR3.crop_to_roi(OCR3, img, [-50, -20, 500, 400])
    assert roi.size > 0
    assert roi.shape[0] <= 100
    assert roi.shape[1] <= 200


def test_crop_to_roi_normal_box():
    img = np.zeros((100, 200, 3), dtype=np.uint8)
    roi = OCR3.crop_to_roi(OCR3, img, [10, 10, 60, 40])
    assert roi.shape[0] == 30
    assert roi.shape[1] == 50
