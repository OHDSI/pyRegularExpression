from typing import Callable, Sequence, Any, Dict, List, Tuple

# import your regex‐finder functions
from pyregularexpression.algorithm_validation_finder import find_algorithm_validation_v1
from pyregularexpression.attrition_criteria_finder import find_attrition_criteria_v1
from pyregularexpression.comparator_cohort_finder import find_comparator_cohort_v1
from pyregularexpression.data_source_type_finder import find_data_source_type_v1
from pyregularexpression.eligibility_criteria_finder import find_eligibility_criteria_v1
from pyregularexpression.entry_event_finder import find_entry_event_v1
from pyregularexpression.exclusion_rule_finder import find_exclusion_rule_v1
from pyregularexpression.exit_criterion_finder import find_exit_criterion_v1
from pyregularexpression.exposure_definition_finder import find_exposure_definition_v1
from pyregularexpression.follow_up_period_finder import find_follow_up_period_v1
from pyregularexpression.healthcare_setting_finder import find_healthcare_setting_v1
from pyregularexpression.inclusion_rule_finder import find_inclusion_rule_v1
from pyregularexpression.index_date_finder import find_index_date_v1
from pyregularexpression.medical_code_finder import find_medical_code_v1
from pyregularexpression.outcome_definition_finder import find_outcome_definition_v1
from pyregularexpression.outcome_endpoints_finder import find_outcome_endpoints_v1
from pyregularexpression.severity_definition_finder import find_severity_definition_v1

__all__ = [
    "REGEX_FUNCS_PHENOTYPE_ALGORITHM_1",
    "apply_regex_funcs",
]

# assemble into a list for iteration
REGEX_FUNCS_PHENOTYPE_ALGORITHM_1 = [
    find_algorithm_validation_v1,
    find_attrition_criteria_v1,
    find_comparator_cohort_v1,
    find_data_source_type_v1,
    find_eligibility_criteria_v1,
    find_entry_event_v1,
    find_exclusion_rule_v1,
    find_exit_criterion_v1,
    find_exposure_definition_v1,
    find_follow_up_period_v1,
    find_healthcare_setting_v1,
    find_inclusion_rule_v1,
    find_index_date_v1,
    find_medical_code_v1,
    find_outcome_definition_v1,
    find_outcome_endpoints_v1,
    find_severity_definition_v1,
]


def apply_regex_funcs(
    text: str,
    regex_funcs: Sequence[Callable[..., List[Tuple[int,int,str]]]]
) -> Dict[str, Any]:
    """
    Apply each regex function in `regex_funcs` to `text`.

    Returns a dict:
      - 'matches': { func_name: [(start, end, snippet), …], … }
      - 'any_match': True if any function returned a non‐empty list
    """
    results: Dict[str, List[Tuple[int,int,str]]] = {}
    for fn in regex_funcs:
        try:
            # most of these take only `text`
            matches = fn(text)
        except TypeError:
            # in case a signature is different, e.g. extra args
            matches = fn(text)  # adjust as needed
        results[fn.__name__] = matches

    return {
        "matches": results,
        "any_match": any(bool(v) for v in results.values()),
    }
