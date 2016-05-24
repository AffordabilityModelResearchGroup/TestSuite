import hashlib
import json
import math

from django.conf import settings
from django.core.cache import cache

from v2 import constants
from v2.models import PovertyGuidelineModel, MedianFamilyIncomeModel, StateNeedGrantMaxAwardModel, \
    StateNeedGrantDistributionScheduleModel, TuitionCostsModel, NonTuitionCostsModel, InstitutionModel
from v2.scenario import KEY_POVERTY_GUIDELINE, KEY_MEDIAN_FAMILY_INCOME, KEY_DISCRETIONARY_INCOME, \
    KEY_STATE_NEED_GRANT_MAX_AWARD, KEY_STATE_NEED_GRANT_DISTRIBUTION_SCHEDULE
from v2.transform.db_import import DBImportTransform
from v2.transform.discretionary_income import DiscretionaryIncomeTransform

__author__ = 'gautam'


def transform_if_not_exists(scenario, key, transform):
    """
    Transform the scenario if he key doesn't exist.
    (Scenario, str, BaseTransform) -> Scenario
    :type scenario: v2.scenario.Scenario
    :param scenario: the scenario to check
    :type key: str
    :param key:
    :type transform: BaseTransform
    :param transform: an instance of BaseTransform
    :return transformed copy of the scenario
    :rtype Scenario
    """
    if scenario.get(key):
        return scenario
    else:
        return transform.transform(scenario)


def _db_transform_(scenario, key, model_cls, **filterargs):
    transform = DBImportTransform(model_cls, key)
    transform.filter(**filterargs)
    return transform_if_not_exists(scenario, key=key, transform=transform)


def import_poverty_guideline(scenario):
    new_scenario = _db_transform_(scenario=scenario,
                                  key=KEY_POVERTY_GUIDELINE,
                                  model_cls=PovertyGuidelineModel,
                                  year=int(scenario[constants.CALENDAR_YEAR]))
    return new_scenario


def import_median_family_income(scenario):
    new_scenario = _db_transform_(scenario=scenario,
                                  key=KEY_MEDIAN_FAMILY_INCOME,
                                  model_cls=MedianFamilyIncomeModel,
                                  state=scenario[constants.STATE],
                                  year=int(scenario[constants.CALENDAR_YEAR]))

    return new_scenario


def import_state_need_grant_max_award(scenario):
    return _db_transform_(scenario=scenario,
                          key=KEY_STATE_NEED_GRANT_MAX_AWARD,
                          model_cls=StateNeedGrantMaxAwardModel,
                          academic_year=int(scenario.get(constants.CALENDAR_YEAR)),
                          institution_type=scenario.get(constants.INSTITUTION_TYPE))


def import_state_need_grant_distribution_schedule(scenario):
    return _db_transform_(scenario=scenario,
                          key=KEY_STATE_NEED_GRANT_DISTRIBUTION_SCHEDULE,
                          model_cls=StateNeedGrantDistributionScheduleModel,
                          academic_year=int(scenario.get(constants.CALENDAR_YEAR)))


def compute_discretionary_income(scenario, poverty_guideline, median_family_income):
    key = (poverty_guideline, median_family_income)
    if not scenario.has_key(KEY_DISCRETIONARY_INCOME):
        scenario[KEY_DISCRETIONARY_INCOME] = {}
    if not scenario[KEY_DISCRETIONARY_INCOME].has_key(key):
        DiscretionaryIncomeTransform(xrange(1, 201), median_family_income, poverty_guideline).transform(scenario)
    return scenario[KEY_DISCRETIONARY_INCOME].get(key)


def _compute_cost_of_attendance(total_tuition, non_tuition, tuition_adjustment):
    avg_tuition = math.floor(sum(total_tuition) / len(total_tuition))
    avg_non_tuition = math.floor(sum(non_tuition) / len(non_tuition))
    if tuition_adjustment:
        avg_tuition = math.floor(avg_tuition + (avg_tuition * tuition_adjustment / 100))
    return {
        constants.TUITION: avg_tuition,
        constants.NON_TUITION: avg_non_tuition
    }


def compute_cost_of_attendance(year, state, living_status, institution_type, tuition_cost_adjustment=0):
    self_hash = hashlib.md5(json.dumps({
        constants.YEAR: year,
        constants.STATE: state,
        constants.LIVING_STATUS: living_status,
        constants.INSTITUTION_TYPE: institution_type,
        'computation_name': 'cost_of_attendance'
    })).hexdigest()

    cost_of_attendance = cache.get(self_hash)
    if not cost_of_attendance:
        institution_objects = InstitutionModel.objects.filter(institution_type=institution_type,
                                                              state=state)
        # TODO remove temporary workaround for missing state
        if len(institution_objects) < 1:
            institution_objects = InstitutionModel.objects.filter(institution_type=institution_type)

        institutions = [institution.institution for institution in institution_objects]

        tuition_costs = TuitionCostsModel.objects.filter(institution__in=institutions, academic_year=year)

        non_tuition_costs = NonTuitionCostsModel.objects.filter(state=state,
                                                                academic_year=year,
                                                                living_status=living_status)
        # TODO remove temporary workaround for missing state
        if len(non_tuition_costs) < 1:
            non_tuition_costs = NonTuitionCostsModel.objects.filter(academic_year=year,
                                                                    living_status=living_status)

        cost_of_attendance = _compute_cost_of_attendance(
            [t.tuition_and_fees for t in tuition_costs],
            [t.total() for t in non_tuition_costs],
            tuition_cost_adjustment
        )

        cache.set(self_hash, cost_of_attendance, settings.CACHE_LENGTH)

    return cost_of_attendance


def compute_disbursement(principal, interest, time_to_graduate):
    P = float(principal)
    N = float(time_to_graduate)
    I = float(interest)
    if I > 0:
        onePlusIToTheNth = math.pow(1 + I, N)
        step1 = P
        step2 = I * onePlusIToTheNth
        step3 = onePlusIToTheNth - 1
        A = step1 * step2 / step3
    else:
        A = P / N
    return A


def compute_interest(annual_deposit, interest, years_of_saving, time_to_graduate):
    A = float(annual_deposit)
    i = float(interest)
    n = years_of_saving
    if i > 0:
        part1 = (A / 12)
        part2 = math.pow((1 + i / 12), n * 12) - 1
        part3 = (i / 12)
        F = part1 * part2 / part3
    else:
        F = A * n
    disbursement = compute_disbursement(F, interest, time_to_graduate)
    return disbursement


def compute_median_family_income(scenario):
    import_median_family_income(scenario)
    q_median_family_income = scenario.get(KEY_MEDIAN_FAMILY_INCOME)[0]
    family_size = int(scenario.get(constants.FAMILY_SIZE))
    adjustments = [0, 0.52, 0.68, 0.84, 1.0, 1.16, 1.32, 0.03]
    if 0 <= family_size <= 6:
        return q_median_family_income.income * adjustments[family_size]
    else:
        family_of_6 = q_median_family_income.income * adjustments[6]
        extra_members = family_size - 6
        return family_of_6 + (adjustments[7] * q_median_family_income.income * extra_members)