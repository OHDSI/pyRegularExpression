"""PyTest suite for healthcare_setting_finder.py"""
import pytest

from pyregularexpression.healthcare_setting_finder import (
    find_healthcare_setting_v1,
    find_healthcare_setting_v2,
    find_healthcare_setting_v3,
    find_healthcare_setting_v4,
    find_healthcare_setting_v5,
)

FINDERS = [
    find_healthcare_setting_v1,
    find_healthcare_setting_v2,
    find_healthcare_setting_v3,
    find_healthcare_setting_v4,
    find_healthcare_setting_v5,
]

# ─────────────────────────────
# Example corpora
# ─────────────────────────────
POSITIVE_EXAMPLES = [
    "Patients were admitted to the ICU of an urban tertiary-care hospital.",
    "The study was conducted in five primary care clinics across rural settings.",
    "Data were extracted from outpatient ambulatory clinic visits.",
    "Participants were recruited from the emergency department (ED) ward.",
    "We analysed inpatient hospital records from a community teaching hospital.",
    # Add headings to test HEADING_SET_RE
    "Setting: Healthcare settings in urban areas.",
    "Study Setting: The trial was conducted in various hospitals.",
    "Research Setting: Data was collected from inpatient care units."
]

NEGATIVE_EXAMPLES = [
    "A real‑world setting is difficult to reproduce in simulation studies.",
    "This analysis focuses on the setting of care coordination rather than location.",
    "Results are applicable to various research settings.",
]

# ─────────────────────────────
# Tests
# ─────────────────────────────
@pytest.mark.parametrize("finder", FINDERS)
@pytest.mark.parametrize("text", POSITIVE_EXAMPLES)
def test_positive_cases(finder, text):
    """All variants should match at least one span in positive examples."""
    assert finder(text), f"{finder.__name__} failed to match on: {text}"


@pytest.mark.parametrize("text", NEGATIVE_EXAMPLES)
def test_high_precision_negative(text):
    """Variant 5 should remain silent on generic or abstract 'setting' phrases."""
    assert not find_healthcare_setting_v5(text), f"v5 falsely matched: {text}"
