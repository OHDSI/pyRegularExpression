# tests/test_recruitment_timeline_finder.py
"""
Complete test suite for recruitment_timeline_finder.py.
Covers five variants (v1–v5):
    • v1 – high recall: recruitment/enrolment cue + date/date-range
    • v2 – cue + explicit date range separator
    • v3 – inside Recruitment/Study Period/Timeline heading block
    • v4 – v2 + follow-up phrase in same sentence
    • v5 – tight template form
"""
import pytest
from pyregularexpression.recruitment_timeline_finder import (
    find_recruitment_timeline_v1,
    find_recruitment_timeline_v2,
    find_recruitment_timeline_v3,
    find_recruitment_timeline_v4,
    find_recruitment_timeline_v5,
)

# ────────────────────────────────────
# Robust Tests for v1 (High Recall)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive: recruited + date
        ("Patients were recruited in March 2015.", True, "v1_pos_simple_date"),
        # Positive: enrolment with range
        ("Enrolment occurred from January 2012 to December 2014.", True, "v1_pos_range"),
        # Trap: recruitment difficulty statement
        ("Recruitment was challenging in rural hospitals.", False, "v1_neg_trap_challenging"),
        # Negative: unrelated date mention
        ("The analysis was performed in 2019.", False, "v1_neg_analysis_date"),
    ],
)
def test_find_recruitment_timeline_v1(text, should_match, test_id):
    matches = find_recruitment_timeline_v1(text)
    assert bool(matches) == should_match, f"v1 failed for {test_id}"


# ────────────────────────────────────
# Robust Tests for v2 (Cue + Range Separator)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive: recruited with "to" range
        ("Participants were recruited May 2010 to July 2012.", True, "v2_pos_to_range"),
        # Positive: enrolled with en-dash
        ("Subjects were enrolled 2011–2013 across three sites.", True, "v2_pos_en_dash"),
        # Negative: recruitment but no separator
        ("Subjects were enrolled in 2016.", False, "v2_neg_no_separator"),
        # Negative: date range but no recruitment cue
        ("The study spanned 2008–2010 with follow-up later.", False, "v2_neg_no_cue"),
    ],
)
def test_find_recruitment_timeline_v2(text, should_match, test_id):
    matches = find_recruitment_timeline_v2(text, window=6)

    assert bool(matches) == should_match, f"v2 failed for {test_id}"


# ────────────────────────────────────
# Lighter Tests for v3 (Heading Block)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive: inside Recruitment heading
        ("Recruitment period:\nPatients were recruited between 2010 and 2012.\n", True, "v3_pos_heading_recruitment"),
        # Positive: inside Study period heading
        ("Study period:\nEnrolment occurred from Jan 2011 to Dec 2013.\n", True, "v3_pos_heading_study_period"),
        # Negative: block empty
        ("Recruitment period:\n(No recruitment dates provided)\n", False, "v3_neg_empty_block"),
        # Negative: recruitment mentioned outside heading
        ("Patients were enrolled in 2014.\n\nRecruitment period:\nNot specified.", False, "v3_neg_outside_block"),
    ],
)
def test_find_recruitment_timeline_v3(text, should_match, test_id):
    matches = find_recruitment_timeline_v3(text)
    assert bool(matches) == should_match, f"v3 failed for {test_id}"


# ────────────────────────────────────
# Lighter Tests for v4 (Range + Follow-up Cue)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive: recruited with date range + follow-up
        ("Patients were recruited from Jan 2012 to Jun 2013 and followed for 12 months.", True, "v4_pos_range_followup"),
        # Positive: enrolment range + median follow-up phrase
        ("Enrolment occurred 2010–2011; median follow-up was 5 years.", True, "v4_pos_followup_phrase"),
        # Negative: recruitment range but no follow-up
        ("Participants were recruited March 2014–July 2015.", False, "v4_neg_no_followup"),
        # Negative: follow-up mentioned but no recruitment range
        ("Follow-up lasted 3 years after randomisation.", False, "v4_neg_followup_no_recruitment"),
    ],
)
def test_find_recruitment_timeline_v4(text, should_match, test_id):
    matches = find_recruitment_timeline_v4(text, window=8)
    assert bool(matches) == should_match, f"v4 failed for {test_id}"


# ────────────────────────────────────
# Lighter Tests for v5 (Tight Template)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive: strict template form
        ("Enrolled Jan 2010–Dec 2012; each followed 24 months.", True, "v5_pos_template_strict"),
        # Positive: slight variation still matches
        ("Enrolment Feb 2013–May 2015; patients were followed 12 years.", True, "v5_pos_template_variant"),
        # Negative: lacks follow-up duration
        ("Enrolled March 2010–April 2012.", False, "v5_neg_no_followup"),
        # Negative: vague phrase
        ("Participants were recruited over time and monitored.", False, "v5_neg_loose_phrase"),
    ],
)
def test_find_recruitment_timeline_v5(text, should_match, test_id):
    matches = find_recruitment_timeline_v5(text)
    assert bool(matches) == should_match, f"v5 failed for {test_id}"
