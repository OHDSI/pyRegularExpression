"""
Smoke tests for entry_event_finder variants.

This suite checks detection of entry events across five tiers (v1–v5),
ranging from high-recall pattern matching to strict template-based
matching. Each level adds contextual or structural constraints to reduce false positives.
"""

import pytest
from pyregularexpression.entry_event_finder import (
    find_entry_event_v1,
    find_entry_event_v2,
    find_entry_event_v3,
    find_entry_event_v4,
    find_entry_event_v5,
)

# ─────────────────────────────
# v1 – high recall (any entry-event cue)
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # ✅ Original Positives
        ("Entry event was first myocardial infarction between 2010 and 2015.", True, "v1_pos_first_mi"),  # mentions entry + MI
        ("Patients were eligible upon hospitalization for heart failure.", True, "v1_pos_eligible_hosp"),  # "hospitalization"
        ("Patients experienced myocardial infarctions during follow‑up.", True, "v1_pos_broad_match"),  # has MI cue
        ("The study relied on data entry by clinicians.", False, "v1_fix_data_entry_not_entry_event"),  # ❌ corrected: no entry event

        # ✅ New Positives
        ("Three patients experienced myocardial infarction during or within 36 hours of operation.", True, "v1_pubmed_mi_36h"),  # MI cue
        ("Approximately 8.9% of patients experienced myocardial infarction following PCI.", True, "v1_pubmed_post_pci"),  # MI cue
        ("Eighteen patients experienced myocardial infarction (3.8%).", True, "v1_pubmed_simple_mi"),  # MI cue
        ("69 patients in the conservative strategy group experienced myocardial infarction.", True, "v1_pubmed_strategy_arm"),  # MI cue
        ("Eleven patients (45.8%) experienced myocardial infarction (MI).", True, "v1_pubmed_stat_mi"),  # MI cue
        ("Patients with one inpatient diagnosis of diabetes were included.", True, "v1_ohdsi_inpatient_diag"),  # diagnosis cue
        ("Cohort entry was defined by the first inpatient visit.", True, "v1_ohdsi_entry_by_visit"),  # "cohort entry"
        ("Enter the cohort at the time of COVID-19 diagnosis.", True, "v1_ohdsi_entry_covid_diag"),  # "cohort" + "diagnosis"
        ("Persons hospitalized with influenza were selected using inpatient visit records.", True, "v1_ohdsi_influenza_visit"),  # hospitalization cue
        ("Inclusion was based on an admission for heart failure.", True, "v1_ohdsi_admission_based_incl"),  # "admission"

        # 🆕 Additional v1 edge‑cases
        ("Adverse event was recorded in all patients.", False, "v1_neg_adverse_event"),  # false positive trap
        ("We recruited patients at their first admission.", True, "v1_pos_first_admission"),  # first admission → match
        ("Initial cohort entry occurred on day 0.", True, "v1_pos_initial_cohort_entry"),  # initial cohort entry → match

        # ❌ Negatives (Corrected and Verified)
        ("We excluded patients with incomplete data records.", False, "v1_neg_exclusion"),  # exclusion context
        ("Diagnosis was used only for follow-up confirmation.", False, "v1_neg_followup_only"),  # diagnosis ≠ entry event here
        ("Patients were monitored post-discharge only.", False, "v1_neg_post_discharge"),  # no qualifying event
        ("No hospitalizations were used as entry events.", False, "v1_neg_negated_entry_event"),  # explicitly says NOT used
    ]
)
def test_find_entry_event_v1(text, should_match, test_id):
    matches = find_entry_event_v1(text)
    assert bool(matches) == should_match, f"v1 failed for ID: {test_id}"

# ─────────────────────────────
# v2 – cue + inclusion verb nearby
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Patients were eligible upon hospitalization for heart failure.", True, "v2_pos_eligible_hosp"),  # inclusion verb + hospitalization
        ("Cohort entry defined by diagnosis of atrial fibrillation.", True, "v2_pos_entry_defined_by_diagnosis"),  # “defined by” + diagnosis
        ("The study relied on data entry by clinicians.", False, "v2_neg_trap_data_entry"),  # trap: data entry ≠ entry event
        ("Patients experienced myocardial infarctions during follow‑up.", False, "v2_neg_trap_followup"),  # follow-up ≠ cohort entry
        ("Included based on inpatient diagnosis of sepsis.", True, "v2_pubmed_include_inpatient_sepsis"),  # strong inclusion pattern
        ("Selection was based on hospitalization for stroke.", True, "v2_pubmed_selection_stroke"),  # “selection” + cue
        ("Hospitalization occurred but was not used to define cohort.", False, "v2_neg_explicitly_excluded"),  # explicit non-entry use
        ("Patients were enrolled upon diagnosis.", True, "v2_pos_enrolled_upon_diagnosis"),  # “enrolled” + diagnosis
        ("Screening visit confirmed eligibility.", False, "v2_neg_screening_visit"),        # trap: screening visit ≠ entry
    ]
)
def test_find_entry_event_v2(text, should_match, test_id):
    matches = find_entry_event_v2(text)
    assert bool(matches) == should_match, f"v2 failed for ID: {test_id}"


# ─────────────────────────────
# v3 – only inside Entry Event-style heading blocks
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Entry Event:\nPatients included upon hospitalization.", True, "v3_pos_heading_entry_event"),  # valid heading block
        ("Cohort Entry:\nThe first diagnosis of stroke was used.", True, "v3_pos_heading_cohort_entry"),  # valid heading
        ("Patients included upon hospitalization.", False, "v3_neg_outside_heading"),  # missing heading
        ("Entry Event:\n\nPatients were hospitalized for influenza.", True, "v3_pos_heading_with_gap_ok"),  # small gap okay
        ("ENTRY EVENT: patients were admitted to ICU.", True, "v3_pos_case_insensitive_heading"),  # case-insensitive
        ("Diagnosis of stroke.", False, "v3_neg_no_heading_plain_text"),  # no heading
        ("Entry Event –\nPatients admitted based on hospitalization.", True, "v3_pos_heading_em_dash"),  # em‑dash instead of colon
    ]
)
def test_find_entry_event_v3(text, should_match, test_id):
    matches = find_entry_event_v3(text)
    assert bool(matches) == should_match, f"v3 failed for ID: {test_id}"

# ─────────────────────────────
# v4 – v2 + “first/initial” qualifier nearby
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("First hospitalization qualified patients for the cohort.", True, "v4_pos_first_hosp_near_qualifier"),  # good
        ("Patients were included after the initial admission.", True, "v4_pos_initial_admission"),  # good
        ("Included upon hospitalization for heart failure.", False, "v4_neg_no_qualifier"),  # no “first/initial”
        ("First visit during follow-up was recorded.", False, "v4_neg_trap_followup"),  # wrong context
        ("Entry based on the first diagnosis of cancer.", True, "v4_pos_first_diagnosis_entry"),  # good
        ("Cohort entry occurred after readmission.", False, "v4_neg_no_qualifier_readmit"),  # no "first/initial"
    ]
)
def test_find_entry_event_v4(text, should_match, test_id):
    matches = find_entry_event_v4(text)
    assert bool(matches) == should_match, f"v4 failed for ID: {test_id}"

# ─────────────────────────────
# v5 – tight template: "Entry event was first …"
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Entry event was first myocardial infarction between 2010 and 2015.", True, "v5_pos_first_mi"),  # perfect template
        ("Entry event was the first hospitalization due to heart failure.", True, "v5_pos_template_match"),  # still matches
        ("Patients included upon first hospitalization.", False, "v5_neg_no_template_phrase"),  # missing full phrase
        ("The first diagnosis was recorded but not labeled as entry event.", False, "v5_neg_missing_template_start"),  # no match
        ("Entry event was first inpatient visit for COPD.", True, "v5_pos_first_inpatient_visit"),  # valid template
        ("The cohort was created based on first hospitalization.", False, "v5_neg_wrong_phrase_order"),  # phrase order wrong
    ]
)
def test_find_entry_event_v5(text, should_match, test_id):
    matches = find_entry_event_v5(text)
    assert bool(matches) == should_match, f"v5 failed for ID: {test_id}"
