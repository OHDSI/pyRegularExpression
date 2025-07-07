# tests/test_treatment_definition_finder.py
"""
Test suite for treatment_definition_finder.py.
Variants (v1–v5):
    • v1 – high recall: any treatment/intervention cue
    • v2 – cue + defining verb
    • v3 – only inside treatment/intervention heading block
    • v4 – v2 + regimen/dose/frequency
    • v5 – tight template (structured dosage/regimen expression)
"""
import pytest
from pyregularexpression.treatment_definition_finder import (
    find_treatment_definition_v1,
    find_treatment_definition_v2,
    find_treatment_definition_v3,
    find_treatment_definition_v4,
    find_treatment_definition_v5,
)

# ───────────────────────────────
# v1 – High Recall (cue only)
# ───────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Patients received treatment with Drug A.", True, "v1_pos_treatment"),
        ("The intervention was described in detail.", True, "v1_pos_intervention"),
        ("Participants had no therapy recorded.", True, "v1_pos_therapy"),
        ("The outcome was mortality after surgery.", False, "v1_neg_outcome_not_treatment"),
    ],
)
def test_find_treatment_definition_v1(text, should_match, test_id):
    matches = find_treatment_definition_v1(text)
    assert bool(matches) == should_match, f"v1 failed for {test_id}"


# ───────────────────────────────
# v2 – Cue + Defining Verb
# ───────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("The treatment was administered orally.", True, "v2_pos_administered"),
        ("Intervention consisted of 3 cycles.", True, "v2_pos_consisted_of"),
        ("Therapy was initiated after diagnosis.", True, "v2_pos_initiated"),
        ("Treatment options were available.", False, "v2_neg_no_defining_verb"),
        ("Patients received no therapy.", True, "v2_pos_received"),
    ],
)
def test_find_treatment_definition_v2(text, should_match, test_id):
    matches = find_treatment_definition_v2(text, window=5)
    assert bool(matches) == should_match, f"v2 failed for {test_id}"


# ───────────────────────────────
# v3 – Heading Block
# ───────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Treatment Regimen:\nPatients received 10 mg daily.", True, "v3_pos_heading_regimen"),
        ("Intervention:\nTherapy was administered weekly.", True, "v3_pos_heading_intervention"),
        ("Methods:\nTreatment was given to all subjects.", False, "v3_neg_wrong_heading"),
    ],
)
def test_find_treatment_definition_v3(text, should_match, test_id):
    matches = find_treatment_definition_v3(text)
    assert bool(matches) == should_match, f"v3 failed for {test_id}"


# ───────────────────────────────
# v4 – Cue + Verb + Regimen/Dose/Frequency
# ───────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Treatment was administered at 10 mg daily for 12 weeks.", True, "v4_pos_mg_daily"),
        ("Intervention consisted of 3 IU/kg every week.", True, "v4_pos_iu_per_kg"),
        ("Therapy was given without dose details.", False, "v4_neg_no_regimen_token"),
        ("Treatment received if needed.", False, "v4_neg_trap_if_needed"),
    ],
)
def test_find_treatment_definition_v4(text, should_match, test_id):
    matches = find_treatment_definition_v4(text, window=6)
    assert bool(matches) == should_match, f"v4 failed for {test_id}"


# ───────────────────────────────
# v5 – Tight Template
# ───────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Drug X 10 mg daily × 12 weeks.", True, "v5_pos_drug_mg_daily"),
        ("Intervention consisted of 20 IU/kg every week.", True, "v5_pos_intervention_iu"),
        ("Treatment group received 50 mg once daily.", True, "v5_pos_treatment_group"),
        ("Patients were treated, but no regimen given.", False, "v5_neg_no_regimen_template"),
    ],
)
def test_find_treatment_definition_v5(text, should_match, test_id):
    matches = find_treatment_definition_v5(text)
    assert bool(matches) == should_match, f"v5 failed for {test_id}"
