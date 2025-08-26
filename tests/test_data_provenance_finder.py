# tests/test_data_provenance_finder.py
"""
Pytest suite for data_provenance_finder.py
Ladder v1–v5:
    • v1 – any provenance/lineage/origin/traceability/audit/source data cue
    • v2 – v1 + paired with verbs like documented/recorded/tracked within ±4 tokens
    • v3 – only inside Methods / Data Source / Provenance heading blocks
    • v4 – v2 + explicit mention of dataset/file/source system
    • v5 – tight template requiring both provenance cue and lineage/audit trail
"""
import pytest
from pyregularexpression.data_provenance_finder import (
    find_data_provenance_v1,
    find_data_provenance_v2,
    find_data_provenance_v3,
    find_data_provenance_v4,
    find_data_provenance_v5,
)

# ─────────────────────────────
# v1 – high recall
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("The provenance of source data was carefully evaluated.", True, "v1_pos_provenance"),
        ("An audit trail ensured data integrity.", True, "v1_pos_audit_trail"),
        ("We assessed lineage across multiple transformations.", True, "v1_pos_lineage"),
        ("The dataset was analyzed without mentioning its history.", False, "v1_neg_no_provenance"),
        ("Traceability was a key component of the study.", True, "v1_pos_traceability"),
    ],
)
def test_v1_data_provenance(text, should_match, test_id):
    matches = find_data_provenance_v1(text)
    assert bool(matches) == should_match, f"v1 failed for {test_id}"


# ─────────────────────────────
# v2 – provenance + verb nearby
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Data provenance was documented in the clinical trial records.", True, "v2_pos_provenance_documented"),
        ("The origin of the data was tracked throughout the ETL process.", True, "v2_pos_origin_tracked"),
        ("Audit trail maintained provenance information.", True, "v2_pos_audit_trail_maintained"),
        ("Provenance of data is important, but no action verb mentioned.", False, "v2_neg_no_verb"),
        ("Lineage was carefully recorded across steps.", True, "v2_pos_lineage_recorded"),
    ],
)
def test_v2_data_provenance(text, should_match, test_id):
    matches = find_data_provenance_v2(text, window=4)
    assert bool(matches) == should_match, f"v2 failed for {test_id}"


# ─────────────────────────────
# v3 – only inside Methods / Data Source / Provenance blocks
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Methods:\nData provenance was evaluated for each dataset.", True, "v3_pos_methods_block"),
        ("Data Source:\nThe lineage of clinical records was documented.", True, "v3_pos_datasource_block"),
        ("Results:\nProvenance of the dataset was briefly discussed.", False, "v3_neg_results_section"),
    ],
)
def test_v3_data_provenance(text, should_match, test_id):
    matches = find_data_provenance_v3(text)
    assert bool(matches) == should_match, f"v3 failed for {test_id}"


# ─────────────────────────────
# v4 – provenance + dataset/file mention
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Data provenance was recorded for each raw data file.", True, "v4_pos_raw_data"),
        ("The lineage was tracked in the clinical record system.", True, "v4_pos_clinical_record"),
        ("Audit trail documented provenance, but no dataset mentioned.", False, "v4_neg_no_dataset"),
    ],
)
def test_v4_data_provenance(text, should_match, test_id):
    matches = find_data_provenance_v4(text, window=6)
    assert bool(matches) == should_match, f"v4 failed for {test_id}"


# ─────────────────────────────
# v5 – tight template
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Data provenance documented in audit trail; lineage maintained across transformations.", True, "v5_pos_template"),
        ("The provenance was recorded and the audit trail ensured lineage.", True, "v5_pos_alt_template"),
        ("Provenance mentioned but without audit trail or lineage.", False, "v5_neg_incomplete"),
    ],
)
def test_v5_data_provenance(text, should_match, test_id):
    matches = find_data_provenance_v5(text)
    assert bool(matches) == should_match, f"v5 failed for {test_id}"
