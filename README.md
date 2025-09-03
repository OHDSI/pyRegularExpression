# pyRegularExpression

This package provides a collection of regular expression-based functions to identify and extract components of the scientific process from text. These components include things like identifying if a text discusses adherence, compliance, eligibility criteria, and more.

## Installation

```bash
pip install pyregularexpression
```

## Available Finder Modules

This package contains a number of finder modules, each designed to find a specific concept in a text. Each module contains one or more functions that implement different versions of a regular expression with varying levels of precision and recall.

Below is a list of the available finder modules and their purpose:

* **Adherence Compliance** (`adherence_compliance_finder.py`): adherence_compliance_finder.py – precision/recall ladder for *treatment adherence / compliance* metrics.
    *   `find_adherence_compliance_v1(text)`
    *   `find_adherence_compliance_v2(text, window=4)`
    *   `find_adherence_compliance_v3(text, block_chars=400)`
    *   `find_adherence_compliance_v4(text, window=12)`
    *   `find_adherence_compliance_v5(text)`
* **Algorithm Validation** (`algorithm_validation_finder.py`): algorithm_validation_finder.py – precision/recall ladder for *algorithm validation* statements.
    *   `find_algorithm_validation_v1(text)`
    *   `find_algorithm_validation_v2(text, window=4)`
    *   `find_algorithm_validation_v3(text, block_chars=400)`
    *   `find_algorithm_validation_v4(text, window=12)`
    *   `find_algorithm_validation_v5(text)`
* **Allocation Concealment** (`allocation_concealment_finder.py`): allocation_concealment_finder.py – precision/recall ladder for *allocation concealment* methods.
    *   `find_allocation_concealment_v1(text)`
    *   `find_allocation_concealment_v2(text, window=4)`
    *   `find_allocation_concealment_v3(text, block_chars=400)`
    *   `find_allocation_concealment_v4(text, window=12)`
    *   `find_allocation_concealment_v5(text)`
* **Attrition Criteria** (`attrition_criteria_finder.py`): attrition_criteria_finder.py – precision/recall ladder for *attrition criteria* (post‑enrolment loss).
    *   `find_attrition_criteria_v1(text)`
    *   `find_attrition_criteria_v2(text, window=4)`
    *   `find_attrition_criteria_v3(text, block_chars=400)`
    *   `find_attrition_criteria_v4(text, window=12)`
    *   `find_attrition_criteria_v5(text)`
* **Background Rationale** (`background_rationale_finder.py`): background_rationale_finder.py – precision/recall ladder for *study background / rationale* statements.
    *   `find_background_rationale_v1(text)`
    *   `find_background_rationale_v2(text, window=4)`
    *   `find_background_rationale_v3(text, block_chars=500)`
    *   `find_background_rationale_v4(text, window=12)`
    *   `find_background_rationale_v5(text)`
* **Baseline Data** (`baseline_data_finder.py`): baseline_data_finder.py – precision/recall ladder for *baseline participant characteristics*.
    *   `find_baseline_data_v1(text)`
    *   `find_baseline_data_v2(text, window=4)`
    *   `find_baseline_data_v3(text, block_chars=400)`
    *   `find_baseline_data_v4(text, window=12)`
    *   `find_baseline_data_v5(text)`
* **Blinding Masking** (`blinding_masking_finder.py`): blinding_masking_finder.py – precision/recall ladder for *blinding / masking* status.
    *   `find_blinding_masking_v1(text)`
    *   `find_blinding_masking_v2(text, window=4)`
    *   `find_blinding_masking_v3(text, block_chars=400)`
    *   `find_blinding_masking_v4(text, window=12)`
    *   `find_blinding_masking_v5(text)`
* **Changes To Outcomes** (`changes_to_outcomes_finder.py`): changes_to_outcomes_finder.py – precision/recall ladder for *changes to prespecified outcomes after trial initiation*.
    *   `find_changes_to_outcomes_v1(text)`
    *   `find_changes_to_outcomes_v2(text, window=4)`
    *   `find_changes_to_outcomes_v3(text, block_chars=400)`
    *   `find_changes_to_outcomes_v4(text, window=12)`
    *   `find_changes_to_outcomes_v5(text)`
* **Comparator Cohort** (`comparator_cohort_finder.py`): comparator_cohort_finder.py – precision/recall ladder for *comparator (control) cohort* statements.
    *   `find_comparator_cohort_v1(text)`
    *   `find_comparator_cohort_v2(text, window=4)`
    *   `find_comparator_cohort_v3(text, block_chars=400)`
    *   `find_comparator_cohort_v4(text, window=12)`
    *   `find_comparator_cohort_v5(text)`
* **Competing Risk Analysis** (`competing_risk_analysis_finder.py`): competing_risk_analysis_finder.py – precision/recall ladder for *competing‑risk analyses*.
    *   `find_competing_risk_analysis_v1(text)`
    *   `find_competing_risk_analysis_v2(text, window=4)`
    *   `find_competing_risk_analysis_v3(text, block_chars=400)`
    *   `find_competing_risk_analysis_v4(text, window=12)`
    *   `find_competing_risk_analysis_v5(text)`
* **Conflict Of Interest** (`conflict_of_interest_finder.py`): conflict_of_interest_finder.py – precision/recall ladder for *conflict‑of‑interest disclosures*.
    *   `find_conflict_of_interest_v1(text)`
    *   `find_conflict_of_interest_v2(text, window=4)`
    *   `find_conflict_of_interest_v3(text, block_chars=400)`
    *   `find_conflict_of_interest_v4(text, window=12)`
    *   `find_conflict_of_interest_v5(text)`
* **Covariate Adjustment** (`covariate_adjustment_finder.py`): covariate_adjustment_finder.py – precision/recall ladder for *covariate adjustment* statements.
    *   `find_covariate_adjustment_v1(text)`
    *   `find_covariate_adjustment_v2(text, window=4)`
    *   `find_covariate_adjustment_v3(text, block_chars=300)`
    *   `find_covariate_adjustment_v4(text, window=6)`
    *   `find_covariate_adjustment_v5(text)`
* **Data Access** (`data_access_finder.py`): data_access_finder.py – precision/recall ladder for *data‑access / availability* statements.
    *   `find_data_access_v1(text)`
    *   `find_data_access_v2(text, window=3)`
    *   `find_data_access_v3(text, block_chars=400)`
    *   `find_data_access_v4(text, window=12)`
    *   `find_data_access_v5(text)`
* **Data Linkage Method** (`data_linkage_method_finder.py`): data_linkage_method_finder.py – precision/recall ladder for *data‑linkage methods*.
    *   `find_data_linkage_method_v1(text)`
    *   `find_data_linkage_method_v2(text, window=3)`
    *   `find_data_linkage_method_v3(text, block_chars=400)`
    *   `find_data_linkage_method_v4(text, window=12)`
    *   `find_data_linkage_method_v5(text)`
* **Data Provenance** (`data_provenance_finder.py`): data_provenance_finder.py – precision/recall ladder for *data provenance*
    *   `find_data_provenance_v1(text)`
    *   `find_data_provenance_v2(text, window=4)`
    *   `find_data_provenance_v3(text, block_chars=400)`
    *   `find_data_provenance_v4(text, window=12)`
    *   `find_data_provenance_v5(text)`
* **Data Safety Monitoring** (`data_safety_monitoring_finder.py`): data_safety_monitoring_finder.py – precision/recall ladder for *Data‑Safety Monitoring* descriptions.
    *   `find_data_safety_monitoring_v1(text)`
    *   `find_data_safety_monitoring_v2(text, window=4)`
    *   `find_data_safety_monitoring_v3(text, block_chars=400)`
    *   `find_data_safety_monitoring_v4(text, window=12)`
    *   `find_data_safety_monitoring_v5(text)`
* **Data Sharing Statement** (`data_sharing_statement_finder.py`): data_sharing_statement_finder.py – precision/recall ladder for *data‑sharing statements*.
    *   `find_data_sharing_statement_v1(text)`
    *   `find_data_sharing_statement_v2(text, window=4)`
    *   `find_data_sharing_statement_v3(text, block_chars=400)`
    *   `find_data_sharing_statement_v4(text, window=12)`
    *   `find_data_sharing_statement_v5(text)`
* **Data Source Type** (`data_source_type_finder.py`): data_source_type_finder.py – precision/recall ladder for *data‑source type* declarations.
    *   `find_data_source_type_v1(text)`
    *   `find_data_source_type_v2(text, window=2)`
    *   `find_data_source_type_v3(text, block_chars=400)`
    *   `find_data_source_type_v4(text, window=12)`
    *   `find_data_source_type_v5(text)`
* **Demographic Restriction** (`demographic_restriction_finder.py`): demographic_restriction_finder.py – precision/recall ladder for demographic‑restriction statements.
    *   `find_demographic_restriction_v1(text)`
    *   `find_demographic_restriction_v2(text, window=4)`
    *   `find_demographic_restriction_v3(text, block_chars=400)`
    *   `find_demographic_restriction_v4(text, window=12)`
    *   `find_demographic_restriction_v5(text)`
* **Dose Response Analysis** (`dose_response_analysis_finder.py`): dose_response_analysis_finder.py – precision/recall ladder for *dose‑response / exposure‑response analyses*.
    *   `find_dose_response_analysis_v1(text)`
    *   `find_dose_response_analysis_v2(text, window=4)`
    *   `find_dose_response_analysis_v3(text, block_chars=400)`
    *   `find_dose_response_analysis_v4(text, window=12)`
    *   `find_dose_response_analysis_v5(text)`
* **Eligibility Criteria** (`eligibility_criteria_finder.py`): eligibility_criteria_finder.py – precision/recall ladder for *inclusion / exclusion eligibility criteria* statements.
    *   `find_eligibility_criteria_v1(text)`
    *   `find_eligibility_criteria_v2(text, window=4)`
    *   `find_eligibility_criteria_v3(text, block_chars=500)`
    *   `find_eligibility_criteria_v4(text, window=12)`
    *   `find_eligibility_criteria_v5(text)`
* **Entry Event** (`entry_event_finder.py`): entry_event_finder.py – precision/recall ladder for *entry‑event* statements.
    *   `find_entry_event_v1(text)`
    *   `find_entry_event_v2(text, window=4)`
    *   `find_entry_event_v3(text, block_chars=400)`
    *   `find_entry_event_v4(text, window=12)`
    *   `find_entry_event_v5(text)`
* **Ethics Approval** (`ethics_approval_finder.py`): ethics_approval_finder.py – precision/recall ladder for *ethics approval & consent* statements.
    *   `find_ethics_approval_v1(text)`
    *   `find_ethics_approval_v2(text, window=4)`
    *   `find_ethics_approval_v3(text, block_chars=400)`
    *   `find_ethics_approval_v4(text, window=12)`
    *   `find_ethics_approval_v5(text)`
* **Event Adjudication** (`event_adjudication_finder.py`): event_adjudication_finder.py – precision/recall ladder for *event‑adjudication descriptions*.
    *   `find_event_adjudication_v1(text)`
    *   `find_event_adjudication_v2(text, window=5)`
    *   `find_event_adjudication_v3(text, block_chars=400)`
    *   `find_event_adjudication_v4(text, window=12)`
    *   `find_event_adjudication_v5(text)`
* **Exclusion Rule** (`exclusion_rule_finder.py`): exclusion_rule_finder.py – precision/recall ladder for *exclusion‑rule* statements.
    *   `find_exclusion_rule_v1(text)`
    *   `find_exclusion_rule_v2(text, window=4)`
    *   `find_exclusion_rule_v3(text, block_chars=400)`
    *   `find_exclusion_rule_v4(text, window=12)`
    *   `find_exclusion_rule_v5(text)`
* **Exit Criterion** (`exit_criterion_finder.py`): exit_criterion_finder.py – precision/recall ladder for *exit-criterion* statements.
    *   `find_exit_criterion_v1(text)`
    *   `find_exit_criterion_v2(text, window=4)`
    *   `find_exit_criterion_v3(text, block_chars=400)`
    *   `find_exit_criterion_v4(text, window=12)`
    *   `find_exit_criterion_v5(text)`
* **Exposure Definition** (`exposure_definition_finder.py`): exposure_definition_finder.py – precision/recall ladder for *exposure definition* statements.
    *   `find_exposure_definition_v1(text)`
    *   `find_exposure_definition_v2(text, window=4)`
    *   `find_exposure_definition_v3(text, block_chars=400)`
    *   `find_exposure_definition_v4(text, window=12)`
    *   `find_exposure_definition_v5(text)`
* **Follow Up Period** (`follow_up_period_finder.py`): follow_up_period_finder.py – precision/recall ladder for *follow‑up period* definitions.
    *   `find_follow_up_period_v1(text)`
    *   `find_follow_up_period_v2(text, window=4)`
    *   `find_follow_up_period_v3(text, block_chars=400)`
    *   `find_follow_up_period_v4(text, window=12)`
    *   `find_follow_up_period_v5(text)`
* **Funding Statement** (`funding_statement_finder.py`): funding_statement_finder.py – precision/recall ladder for *study funding statements*.
    *   `find_funding_statement_v1(text)`
    *   `find_funding_statement_v2(text, window=4)`
    *   `find_funding_statement_v3(text, block_chars=400)`
    *   `find_funding_statement_v4(text, window=12)`
    *   `find_funding_statement_v5(text)`
* **Generalizability** (`generalizability_finder.py`): generalizability_finder.py – precision/recall ladder for *generalizability / external validity* statements.
    *   `find_generalizability_v1(text)`
    *   `find_generalizability_v2(text, window=4)`
    *   `find_generalizability_v3(text, block_chars=400)`
    *   `find_generalizability_v4(text, window=12)`
    *   `find_generalizability_v5(text)`
* **Harms Adverse Event** (`harms_adverse_event_finder.py`): harms_adverse_event_finder.py – precision/recall ladder for *harms / adverse events*.
    *   `find_harms_adverse_event_v1(text)`
    *   `find_harms_adverse_event_v2(text, window=4)`
    *   `find_harms_adverse_event_v3(text, block_chars=400)`
    *   `find_harms_adverse_event_v4(text, window=12)`
    *   `find_harms_adverse_event_v5(text)`
* **Healthcare Setting** (`healthcare_setting_finder.py`): healthcare_setting_finder.py – precision/recall ladder for *health‑care setting* statements.
    *   `find_healthcare_setting_v1(text)`
    *   `find_healthcare_setting_v2(text, window=3)`
    *   `find_healthcare_setting_v3(text, block_chars=400)`
    *   `find_healthcare_setting_v4(text, window=12)`
    *   `find_healthcare_setting_v5(text)`
* **Inclusion Rule** (`inclusion_rule_finder.py`): inclusion_rule_finder.py – precision/recall ladder for *inclusion‑rule* statements.
    *   `find_inclusion_rule_v1(text)`
    *   `find_inclusion_rule_v2(text, window=4)`
    *   `find_inclusion_rule_v3(text, block_chars=400)`
    *   `find_inclusion_rule_v4(text, window=12)`
    *   `find_inclusion_rule_v5(text)`
* **Index Date** (`index_date_finder.py`): index_date_finder.py – precision/recall ladder for *index‑date definition* statements.
    *   `find_index_date_v1(text)`
    *   `find_index_date_v2(text, window=4)`
    *   `find_index_date_v3(text, block_chars=400)`
    *   `find_index_date_v4(text, window=12)`
    *   `find_index_date_v5(text)`
* **Interim Analysis Stopping Rules** (`interim_analysis_stopping_rules_finder.py`): interim_analysis_stopping_rules_finder.py – multi-tiered finder for interim analysis stopping rules.
    *   `find_stopping_rule_v1(text)`
    *   `find_stopping_rule_v2(text)`
    *   `find_stopping_rule_v3(text)`
* **Interventions** (`interventions_finder.py`): interventions_finder.py – precision/recall ladder for *interventions / treatments* delivered to study arms.
    *   `find_interventions_v1(text)`
    *   `find_interventions_v2(text, window=4)`
    *   `find_interventions_v3(text, block_chars=400)`
    *   `find_interventions_v4(text, window=12)`
    *   `find_interventions_v5(text)`
* **Limitations** (`limitations_finder.py`): limitations_finder.py – precision/recall ladder for *study limitations* sections.
    *   `find_limitations_v1(text)`
    *   `find_limitations_v2(text, window=4)`
    *   `find_limitations_v3(text, block_chars=400)`
    *   `find_limitations_v4(text, window=12)`
    *   `find_limitations_v5(text)`
* **Losses Exclusion** (`losses_exclusion_finder.py`): losses_exclusion_finder.py – precision/recall ladder for *losses and exclusions after allocation*.
    *   `find_losses_exclusion_v1(text)`
    *   `find_losses_exclusion_v2(text, window=4)`
    *   `find_losses_exclusion_v3(text, block_chars=500)`
    *   `find_losses_exclusion_v4(text, window=12)`
    *   `find_losses_exclusion_v5(text)`
* **Medical Code** (`medical_code_finder.py`): medical_code_finder.py – precision/recall ladder for *medical code* statements.
    *   `find_medical_code_v1(text)`
    *   `find_medical_code_v2(text, window=5)`
    *   `find_medical_code_v3(text, block_chars=300)`
    *   `find_medical_code_v4(text)`
    *   `find_medical_code_v5(text)`
* **Missing Data Handling** (`missing_data_handling_finder.py`): missing_data_handling_finder.py – precision/recall ladder for *missing‑data handling methods*.
    *   `find_missing_data_handling_v1(text)`
    *   `find_missing_data_handling_v2(text, window=4)`
    *   `find_missing_data_handling_v3(text, block_chars=400)`
    *   `find_missing_data_handling_v4(text, window=12)`
    *   `find_missing_data_handling_v5(text)`
* **Numbers Analyzed** (`numbers_analyzed_finder.py`): numbers_analyzed_finder.py – precision/recall ladder for *numbers analysed* in each analysis population.
    *   `find_numbers_analyzed_v1(text)`
    *   `find_numbers_analyzed_v2(text, window=4)`
    *   `find_numbers_analyzed_v3(text, block_chars=400)`
    *   `find_numbers_analyzed_v4(text, window=12)`
    *   `find_numbers_analyzed_v5(text)`
* **Objective Hypothesis** (`objective_hypothesis_finder.py`): objective_hypothesis_finder.py – precision/recall ladder for *study objectives / hypotheses* statements.
    *   `find_objective_hypothesis_v1(text)`
    *   `find_objective_hypothesis_v2(text, window=3)`
    *   `find_objective_hypothesis_v3(text, block_chars=400)`
    *   `find_objective_hypothesis_v4(text, window=12)`
    *   `find_objective_hypothesis_v5(text)`
* **Outcome Ascertainment** (`outcome_ascertainment_finder.py`): outcome_ascertainment_finder.py – precision/recall ladder for *outcome ascertainment* statements.
    *   `find_outcome_ascertainment_v1(text)`
    *   `find_outcome_ascertainment_v2(text, window=4)`
    *   `find_outcome_ascertainment_v3(text, block_chars=400)`
    *   `find_outcome_ascertainment_v4(text, window=12)`
    *   `find_outcome_ascertainment_v5(text)`
* **Outcome Definition** (`outcome_definition_finder.py`): outcome_definition_finder.py – precision/recall ladder for *outcome definition* statements.
    *   `find_outcome_definition_v1(text)`
    *   `find_outcome_definition_v2(text, window=4)`
    *   `find_outcome_definition_v3(text, block_chars=400)`
    *   `find_outcome_definition_v4(text, window=12)`
    *   `find_outcome_definition_v5(text)`
* **Outcome Endpoints** (`outcome_endpoints_finder.py`): outcome_endpoints_finder.py – precision/recall ladder for *primary and secondary outcomes / endpoints* statements.
    *   `find_outcome_endpoints_v1(text)`
    *   `find_outcome_endpoints_v2(text, window=4)`
    *   `find_outcome_endpoints_v3(text, block_chars=500)`
    *   `find_outcome_endpoints_v4(text, window=12)`
    *   `find_outcome_endpoints_v5(text)`
* **Participant Flow** (`participant_flow_finder.py`): participant_flow_finder.py – precision/recall ladder for *participant flow* statements (CONSORT flow).
    *   `find_participant_flow_v1(text)`
    *   `find_participant_flow_v2(text, window=4)`
    *   `find_participant_flow_v3(text, block_chars=600)`
    *   `find_participant_flow_v4(text, window=12)`
    *   `find_participant_flow_v5(text)`
* **Propensity Score Method** (`propensity_score_method_finder.py`): propensity_score_method_finder.py – precision/recall ladder for *propensity-score methods*.
    *   `find_propensity_score_method_v1(text)`
    *   `find_propensity_score_method_v2(text, window=4)`
    *   `find_propensity_score_method_v3(text, block_chars=400)`
    *   `find_propensity_score_method_v4(text, window=12)`
    *   `find_propensity_score_method_v5(text)`
* **Random Sequence Generation** (`random_sequence_generation_finder.py`): random_sequence_generation_finder.py – precision/recall ladder for *random allocation-sequence generation* methods.
    *   `find_random_sequence_generation_v1(text)`
    *   `find_random_sequence_generation_v2(text, window=4)`
    *   `find_random_sequence_generation_v3(text, block_chars=400)`
    *   `find_random_sequence_generation_v4(text, window=12)`
    *   `find_random_sequence_generation_v5(text)`
* **Randomization Implementation** (`randomization_implementation_finder.py`): randomization_implementation_finder.py – precision/recall ladder for *randomization implementation* (who generated sequence, who enrolled, who assigned).
    *   `find_randomization_implementation_v1(text)`
    *   `find_randomization_implementation_v2(text, window=4)`
    *   `find_randomization_implementation_v3(text, block_chars=500)`
    *   `find_randomization_implementation_v4(text, window=12)`
    *   `find_randomization_implementation_v5(text)`
* **Randomization Type Restriction** (`randomization_type_restriction_finder.py`): randomization_type_restriction_finder.py – precision/recall ladder for *randomization type / restrictions* (blocking, stratification, ratio).
    *   `find_randomization_type_restriction_v1(text)`
    *   `find_randomization_type_restriction_v2(text, window=4)`
    *   `find_randomization_type_restriction_v3(text, block_chars=400)`
    *   `find_randomization_type_restriction_v4(text, window=12)`
    *   `find_randomization_type_restriction_v5(text)`
* **Recruitment Timeline** (`recruitment_timeline_finder.py`): recruitment_timeline_finder.py – precision/recall ladder for *recruitment period / timeline*.
    *   `find_recruitment_timeline_v1(text)`
    *   `find_recruitment_timeline_v2(text, window=4)`
    *   `find_recruitment_timeline_v3(text, block_chars=500)`
    *   `find_recruitment_timeline_v4(text, window=12)`
    *   `find_recruitment_timeline_v5(text)`
* **Risk Of Bias Assessment** (`risk_of_bias_assessment_finder.py`): risk_of_bias_assessment_finder.py – precision/recall ladder for *risk‑of‑bias assessments* in systematic reviews.
    *   `find_risk_of_bias_assessment_v1(text)`
    *   `find_risk_of_bias_assessment_v2(text, window=4)`
    *   `find_risk_of_bias_assessment_v3(text, block_chars=400)`
    *   `find_risk_of_bias_assessment_v4(text, window=12)`
    *   `find_risk_of_bias_assessment_v5(text)`
* **Sensitivity Analysis** (`sensitivity_analysis_finder.py`): sensitivity_analysis_finder.py – precision/recall ladder for *sensitivity analysis* statements.
    *   `find_sensitivity_analysis_v1(text)`
    *   `find_sensitivity_analysis_v2(text, window=4)`
    *   `find_sensitivity_analysis_v3(text, block_chars=400)`
    *   `find_sensitivity_analysis_v4(text, window=12)`
    *   `find_sensitivity_analysis_v5(text)`
* **Settings Locations** (`settings_locations_finder.py`): settings_locations_finder.py – precision/recall ladder for *study settings / locations*
    *   `find_settings_locations_v1(text)`
    *   `find_settings_locations_v2(text, window=4)`
    *   `find_settings_locations_v3(text, block_chars=400)`
    *   `find_settings_locations_v4(text, window=12)`
    *   `find_settings_locations_v5(text)`
* **Severity Definition** (`severity_definition_finder.py`): severity_definition_finder.py – precision/recall ladder for *severity definition* statements.
    *   `find_severity_definition_v1(text)`
    *   `find_severity_definition_v2(text, window=4)`
    *   `find_severity_definition_v3(text, block_chars=400)`
    *   `find_severity_definition_v4(text, window=12)`
    *   `find_severity_definition_v5(text)`
* **Similarity Of Interventions** (`similarity_of_interventions_finder.py`): similarity_of_interventions_finder.py – precision/recall ladder for *similarity of interventions*.
    *   `find_similarity_of_interventions_v1(text)`
    *   `find_similarity_of_interventions_v2(text, window=4)`
    *   `find_similarity_of_interventions_v3(text, block_chars=400)`
    *   `find_similarity_of_interventions_v4(text, window=12)`
    *   `find_similarity_of_interventions_v5(text)`
* **Statistical Analysis Additional Method** (`statistical_analysis_additional_method_finder.py`): statistical_analysis_additional_method_finder.py – precision/recall ladder for *statistical methods of additional analyses* (secondary, subgroup, exploratory).
    *   `find_statistical_analysis_additional_method_v1(text)`
    *   `find_statistical_analysis_additional_method_v2(text, window=4)`
    *   `find_statistical_analysis_additional_method_v3(text, block_chars=500)`
    *   `find_statistical_analysis_additional_method_v4(text, window=12)`
    *   `find_statistical_analysis_additional_method_v5(text)`
* **Statistical Analysis** (`statistical_analysis_finder.py`): statistical_analysis_finder.py – precision/recall ladder for *statistical analysis* statements.
    *   `find_statistical_analysis_v1(text)`
    *   `find_statistical_analysis_v2(text, window=4)`
    *   `find_statistical_analysis_v3(text, block_chars=300)`
    *   `find_statistical_analysis_v4(text, window=6)`
    *   `find_statistical_analysis_v5(text)`
* **Statistical Analysis Primary Analysis** (`statistical_analysis_primary_analysis_finder.py`): statistical_analysis_primary_analysis_finder.py – precision/recall ladder for *statistical methods of the primary analysis*.
    *   `find_statistical_analysis_primary_analysis_v1(text)`
    *   `find_statistical_analysis_primary_analysis_v2(text, window=4)`
    *   `find_statistical_analysis_primary_analysis_v3(text, block_chars=500)`
    *   `find_statistical_analysis_primary_analysis_v4(text, window=12)`
    *   `find_statistical_analysis_primary_analysis_v5(text)`
* **Study Design** (`study_design_finder.py`): study_design_finder.py – precision/recall ladder for *study design* declarations.
    *   `find_study_design_v1(text)`
    *   `find_study_design_v2(text, window=4)`
    *   `find_study_design_v3(text, block_chars=400)`
    *   `find_study_design_v4(text, window=12)`
    *   `find_study_design_v5(text)`
* **Study Period** (`study_period_finder.py`): study_period_finder.py – precision/recall ladder for *study period* calendar windows.
    *   `find_study_period_v1(text)`
    *   `find_study_period_v2(text, window=4)`
    *   `find_study_period_v3(text, block_chars=400)`
    *   `find_study_period_v4(text, window=12)`
    *   `find_study_period_v5(text)`
* **Subgroup Analysis** (`subgroup_analysis_finder.py`): subgroup_analysis_finder.py – precision/recall ladder for *subgroup / interaction analyses*.
    *   `find_subgroup_analysis_v1(text)`
    *   `find_subgroup_analysis_v2(text, window=4)`
    *   `find_subgroup_analysis_v3(text, block_chars=400)`
    *   `find_subgroup_analysis_v4(text, window=12)`
    *   `find_subgroup_analysis_v5(text)`
* **Treatment Definition** (`treatment_definition_finder.py`): treatment_definition_finder.py – precision/recall ladder for *treatment definition* statements.
    *   `find_treatment_definition_v1(text)`
    *   `find_treatment_definition_v2(text, window=4)`
    *   `find_treatment_definition_v3(text, block_chars=400)`
    *   `find_treatment_definition_v4(text, window=12)`
    *   `find_treatment_definition_v5(text)`
* **Trial Design Changes** (`trial_design_changes_finder.py`): trial_design_changes_finder.py – precision/recall ladder for *changes to trial design/protocol* after initiation.
    *   `find_trial_design_changes_v1(text)`
    *   `find_trial_design_changes_v2(text, window=4)`
    *   `find_trial_design_changes_v3(text, block_chars=400)`
    *   `find_trial_design_changes_v4(text, window=12)`
    *   `find_trial_design_changes_v5(text)`
* **Trial Design** (`trial_design_finder.py`): trial_design_finder.py – precision/recall ladder for *clinical/epidemiological trial or study design* statements.
    *   `find_trial_design_v1(text)`
    *   `find_trial_design_v2(text, window=4)`
    *   `find_trial_design_v3(text, block_chars=400)`
    *   `find_trial_design_v4(text, window=12)`
    *   `find_trial_design_v5(text)`
* **Trial Registration** (`trial_registration_finder.py`): trial_registration_finder.py – precision/recall ladder for *prospective trial registration* statements.
    *   `find_trial_registration_v1(text)`
    *   `find_trial_registration_v2(text, window=4)`
    *   `find_trial_registration_v3(text, block_chars=400)`
    *   `find_trial_registration_v4(text, window=12)`
    *   `find_trial_registration_v5(text)`
* **Washout Period** (`washout_period_finder.py`): washout_period_finder.py – precision/recall ladder for *washout period* definitions.
    *   `find_washout_period_v1(text)`
    *   `find_washout_period_v2(text, window=4)`
    *   `find_washout_period_v3(text, block_chars=400)`
    *   `find_washout_period_v4(text, window=12)`
    *   `find_washout_period_v5(text)`

## Usage

### Finder Functions

Each `*_finder.py` module contains finder functions that return a list of tuples, where each tuple contains the start and end character indices of a match and the matched string itself.

For example, the `adherence_compliance_finder.py` module contains functions to find mentions of treatment adherence or compliance. The functions are named `find_adherence_compliance_v1` through `find_adherence_compliance_v5`, where `v1` is a high-recall version and `v5` is a high-precision version.

Here's an example of how to use one of these functions:

```python
from pyregularexpression.adherence_compliance_finder import find_adherence_compliance_v1

text = "The study measured adherence to the new drug. Adherence was defined as PDC > 0.8."

matches = find_adherence_compliance_v1(text)

for start, end, snippet in matches:
    print(f"Found '{snippet}' at indices {start}-{end}")
```

### Example: Finding Medical Codes

Here is an example of how to use the `medical_code_finder` to extract potential medical codes from a piece of text.

```python
from pyregularexpression.medical_code_finder import find_medical_code_v1

text = "The patient was diagnosed with ICD-10 code I21.0, which is an acute myocardial infarction. The CPT code was 99285."

matches = find_medical_code_v1(text)

for start, end, snippet in matches:
    print(f"Found medical code: {snippet}")

```

### Helper Functions

The package also includes helper functions to apply multiple finder functions at once.

#### `apply_regex_funcs`

This function applies a list of finder functions to a text and returns a dictionary of the results.

```python
from pyregularexpression.apply_regex_functions import apply_regex_funcs
from pyregularexpression.adherence_compliance_finder import find_adherence_compliance_v1
from pyregularexpression.algorithm_validation_finder import find_algorithm_validation_v1

text = "The study measured adherence to the new drug. The algorithm was validated."

results = apply_regex_funcs(text, [find_adherence_compliance_v1, find_algorithm_validation_v1])

print(results)
```

#### `extract_regex_paragraphs_udf`

This function returns a Spark UDF that can be used to extract paragraphs from a text that match any of a list of finder functions.

```python
from pyspark.sql import SparkSession
from pyregularexpression.extract_regex_paragraphs_udf import extract_regex_paragraphs_udf
from pyregularexpression.adherence_compliance_finder import find_adherence_compliance_v1
from pyregularexpression.algorithm_validation_finder import find_algorithm_validation_v1

spark = SparkSession.builder.getOrCreate()

data = [("The study measured adherence to the new drug.\n\nThe algorithm was validated.",)]
df = spark.createDataFrame(data, ["text"])

udf = extract_regex_paragraphs_udf([find_adherence_compliance_v1, find_algorithm_validation_v1])

df.withColumn("matched_paragraphs", udf(df["text"])).show()
```
