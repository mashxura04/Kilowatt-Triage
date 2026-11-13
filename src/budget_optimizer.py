
from itertools import combinations
import math

from src.evaluation import evaluate_school


def validate_budget(budget_usd_2021):
    if (
        isinstance(budget_usd_2021, bool)
        or not isinstance(budget_usd_2021, (int, float))
        or not math.isfinite(budget_usd_2021)
        or budget_usd_2021 < 0
    ):
        raise ValueError(
            "Budget must be a finite, non-negative number."
        )


def get_measure(item):
    return {
        "intervention": item["intervention"],
        "estimated_saving_kwh": (
            item["estimated_energy_saving_kwh"]
        ),
        "investment_cost_usd_2021": (
            item["investment_cost_usd"]
        ),
    }


def build_thermal_candidates(interventions):
    by_name = {
        item["intervention"]: item
        for item in interventions
    }

    candidates = [
        {
            "measures": [],
            "saving_kwh": 0.0,
            "cost_usd_2021": 0.0,
        }
    ]

    insulation = by_name["Insulation"]

    insulation_measure = get_measure(insulation)

    candidates.append({
        "measures": [insulation_measure],
        "saving_kwh": insulation_measure[
            "estimated_saving_kwh"
        ],
        "cost_usd_2021": insulation_measure[
            "investment_cost_usd_2021"
        ],
    })

    boiler_name = {
        "coal": "Efficient coal boiler",
        "gas": "Gas boiler retrofit",
    }.get(
        interventions[0].get("_heating_system")
    )

    if boiler_name is not None:
        boiler = by_name[boiler_name]

        if boiler["compatibility"] == "compatible":
            boiler_measure = get_measure(boiler)

            candidates.append({
                "measures": [
                    insulation_measure,
                    boiler_measure,
                ],
                "saving_kwh": (
                    insulation_measure["estimated_saving_kwh"]
                    + boiler_measure["estimated_saving_kwh"]
                ),
                "cost_usd_2021": (
                    insulation_measure[
                        "investment_cost_usd_2021"
                    ]
                    + boiler_measure[
                        "investment_cost_usd_2021"
                    ]
                ),
            })

    return candidates


def build_electrical_candidates(interventions):
    candidates = [{
        "measures": [],
        "saving_kwh": 0.0,
        "cost_usd_2021": 0.0,
    }]

    for item in interventions:
        if (
            item["reported_saving_basis"] == "electrical"
            and item["compatibility"] == "compatible"
            and item["estimate_status"] == "estimated"
        ):
            measure = get_measure(item)

            candidates.append({
                "measures": [measure],
                "saving_kwh": measure["estimated_saving_kwh"],
                "cost_usd_2021": (
                    measure["investment_cost_usd_2021"]
                ),
            })

    return candidates


def select_best_candidate(candidates, budget):
    feasible = [
        candidate
        for candidate in candidates
        if candidate["cost_usd_2021"] <= budget
    ]

    # Maximize savings. If savings tie, prefer the cheaper package.
    return max(
        feasible,
        key=lambda candidate: (
            candidate["saving_kwh"],
            -candidate["cost_usd_2021"],
        ),
    )


def format_result(candidate, budget):
    cost = candidate["cost_usd_2021"]

    return {
        "selected_measures": candidate["measures"],
        "estimated_savings_kwh": candidate["saving_kwh"],
        "investment_cost_usd_2021": cost,
        "remaining_budget_usd_2021": budget - cost,
        "budget_usd_2021": budget,
    }


def optimize_retrofit_budget(profile, budget_usd_2021):
    validate_budget(budget_usd_2021)

    evaluation = evaluate_school(profile)

    interventions = evaluation["interventions"]

    # Attach the heating system locally for thermal candidate generation.
    interventions = [
        {
            **item,
            "_heating_system": profile["heating_system"],
        }
        for item in interventions
    ]

    thermal_candidates = build_thermal_candidates(
        interventions
    )

    electrical_candidates = build_electrical_candidates(
        interventions
    )

    thermal_result = format_result(
        select_best_candidate(
            thermal_candidates,
            budget_usd_2021,
        ),
        budget_usd_2021,
    )

    electrical_result = format_result(
        select_best_candidate(
            electrical_candidates,
            budget_usd_2021,
        ),
        budget_usd_2021,
    )

    return {
        "budget_usd_2021": budget_usd_2021,
        "cost_basis": (
            "Published 2021 USD reference-school costs; "
            "not adjusted for school floor area."
        ),
        "thermal_optimization": thermal_result,
        "electrical_optimization": electrical_result,
        "limitations": [
            "Thermal and electrical savings are optimized separately.",
            "Boiler savings are treated as post-insulation savings.",
            "Fuel-switch options are excluded from optimization.",
            "Investment costs are historical reference-school costs.",
            "The optimizer considers only interventions with "
            "available, compatible estimates.",
        ],
    }
