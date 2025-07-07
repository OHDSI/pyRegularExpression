# tests/test_settings_locations_finder.py
"""
Pytest suite for settings_locations_finder.py
Ladder v1–v5:
    • v1 – any “setting(s)” mention or “study was conducted” cue
    • v2 – v1 + explicit facility (hospital, clinic, university, community, etc.)
    • v3 – only inside Study Setting / Methods / Participants heading block
    • v4 – v2 + explicit geographic entity (city, country, region)
    • v5 – tight template: “The study was conducted at [facility] in [city], [country]”
"""
import pytest
from pyregularexpression.settings_locations_finder import (
    find_settings_location_v1,
    find_settings_location_v2,
    find_settings_location_v3,
    find_settings_location_v4,
    find_settings_location_v5,
)

# ─────────────────────────────
# v1 – high recall
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Study settings included primary care practices across three regions.", True, "v1_pos_settings"),
        ("The study was conducted among participants recruited online.", True, "v1_pos_conducted"),
        ("Outcomes were reported without reference to study setting.", False, "v1_neg_no_setting"),
        ("The research setting was a large metropolitan area.", True, "v1_pos_research_setting"),
        ("No mention of hospitals or study conduct is made here.", False, "v1_neg_no_cue"),
    ],
)
def test_v1_settings_location(text, should_match, test_id):
    matches = find_settings_location_v1(text)
    assert bool(matches) == should_match, f"v1 failed for {test_id}"


# ─────────────────────────────
# v2 – add facility term
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("The study was conducted at a tertiary hospital.", True, "v2_pos_hospital"),
        ("Participants were recruited from community clinics.", True, "v2_pos_clinic"),
        ("The study was conducted in 2019 with no facility named.", False, "v2_neg_no_facility"),
        ("Conducted at the University Medical Center.", True, "v2_pos_university_medical_center"),
        ("The investigation was carried out nationwide without specific sites.", False, "v2_neg_no_facility_word"),
    ],
)
def test_v2_settings_location(text, should_match, test_id):
    matches = find_settings_location_v2(text, window=5)
    assert bool(matches) == should_match, f"v2 failed for {test_id}"


# ─────────────────────────────
# v3 – only inside Study Setting / Methods / Participants blocks
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Study Setting:\nPatients were enrolled at a university hospital.", True, "v3_pos_setting_block"),
        ("Methods:\nData were collected from rural community clinics.", True, "v3_pos_methods_block"),
        ("Discussion:\nOur findings may not generalize to all populations.", False, "v3_neg_discussion"),
    ],
)
def test_v3_settings_location(text, should_match, test_id):
    matches = find_settings_location_v3(text)
    assert bool(matches) == should_match, f"v3 failed for {test_id}"


# ─────────────────────────────
# v4 – facility + geographic entity
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("The study was conducted at a teaching hospital in New York, USA.", True, "v4_pos_hospital_city_country"),
        ("Data were obtained from primary care clinics in rural India.", True, "v4_pos_clinics_country"),
        ("The study was conducted at a clinic, but no geographic location provided.", False, "v4_neg_no_geo"),
    ],
)
def test_v4_settings_location(text, should_match, test_id):
    matches = find_settings_location_v4(text, window=8)
    assert bool(matches) == should_match, f"v4 failed for {test_id}"


# ─────────────────────────────
# v5 – tight template
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("The study was conducted at the University Hospital in Paris, France.", True, "v5_pos_university_hospital"),
        ("The study was performed at a community clinic in Mumbai, India.", True, "v5_pos_clinic_city_country"),
        ("Settings: patients were enrolled at hospitals and clinics worldwide.", False, "v5_neg_general"),
    ],
)
def test_v5_settings_location(text, should_match, test_id):
    matches = find_settings_location_v5(text)
    assert bool(matches) == should_match, f"v5 failed for {test_id}"
