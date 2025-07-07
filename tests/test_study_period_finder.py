# tests/test_study_period_finder.py
"""
Complete test suite for study_period_finder.py.
Covers five variants (v1–v5):
    • v1 – high recall (any date/year range)
    • v2 – date range + study-term cue within window
    • v3 – inside Study period/Study window heading block
    • v4 – v2 + explicit from/between keyword
    • v5 – tight template
"""
import pytest
from pyregularexpression.study_period_finder import (
    find_study_period_v1,
    find_study_period_v2,
    find_study_period_v3,
    find_study_period_v4,
    find_study_period_v5,
)

# ────────────────────────────────────
# Robust Tests for v1 (High Recall)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Enrollment occurred Jan 2015–Dec 2019 across centers.", True, "v1_pos_month_year_dash"),
        ("Data span 2008–2012 in the registry.", True, "v1_pos_year_en_dash"),
        ("The trial ran from 2000 to 2005.", True, "v1_pos_year_to_year"),
        ("Follow-up 2015–2016 was recorded.", False, "v1_neg_follow_up_trap"),
    ],
)
def test_find_study_period_v1(text, should_match, test_id):
    matches = find_study_period_v1(text)
    assert bool(matches) == should_match, f"v1 failed for {test_id}"


# ────────────────────────────────────
# Robust Tests for v2 (Range + Study-Term Cue)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Data were collected between 2000 and 2005 at three hospitals.", True, "v2_pos_between_years"),
        ("Records from Jan 2015 to Mar 2017 were included.", True, "v2_pos_from_months_years"),
        ("The registry covered 2010–2012.", False, "v2_neg_no_study_term_nearby"),
    ],
)
def test_find_study_period_v2(text, should_match, test_id):
    matches = find_study_period_v2(text, window=5)
    assert bool(matches) == should_match, f"v2 failed for {test_id}"


# ────────────────────────────────────
# Lighter Tests for v3 (Heading Block)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Study period:\nJanuary 2015–June 2018.", True, "v3_pos_heading_block"),
        ("Data collection period -\n2001 to 2004 at two sites.", True, "v3_pos_data_collection_heading"),
        ("Methods:\nThe registry covered 2013–2014.", False, "v3_neg_outside_heading"),
        ("Study window:\n(No dates provided)", False, "v3_neg_empty_block"),
    ],
)
def test_find_study_period_v3(text, should_match, test_id):
    matches = find_study_period_v3(text)
    assert bool(matches) == should_match, f"v3 failed for {test_id}"


# ────────────────────────────────────
# Lighter Tests for v4 (From/Between Keyword)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("The study ran from 2009 to 2013 across multiple centers.", True, "v4_pos_from_years"),
        ("Data were gathered between Mar 2016 and Dec 2018.", True, "v4_pos_between_month_years"),
        ("Study period Jan 2015–Dec 2019.", False, "v4_neg_no_from_or_between"),
        ("Collected across sites 2010–2012.", False, "v4_neg_range_without_keywords"),
    ],
)
def test_find_study_period_v4(text, should_match, test_id):
    matches = find_study_period_v4(text, window=6)
    assert bool(matches) == should_match, f"v4 failed for {test_id}"


# ────────────────────────────────────
# Lighter Tests for v5 (Tight Template)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Study period: Jan 2015–Dec 2019.", True, "v5_pos_study_period_colon"),
        ("Data collection – 2000 to 2005 for all centers.", True, "v5_pos_data_collection_dash"),
        ("Follow-up period: 2015–2016.", False, "v5_neg_follow_up_trap"),
        ("Background period considered: years prior to 2010.", False, "v5_neg_not_template"),
    ],
)
def test_find_study_period_v5(text, should_match, test_id):
    matches = find_study_period_v5(text)
    assert bool(matches) == should_match, f"v5 failed for {test_id}"
