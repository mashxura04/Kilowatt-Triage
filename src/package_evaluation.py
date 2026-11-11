
from src.baseline import calculate_baseline
from src.evaluation import evaluate_school


SEQUENTIAL_BOILER_INTERVENTIONS = {
    "coal": "Efficient coal boiler",
    "gas": "Gas boiler retrofit",
}


def evaluate_retrofit_package(profile):
    """
    Evaluate a conservative sequential retrofit package.

    The package includes:
    1. Insulation.
    2. A compatible conventional boiler upgrade, where supported.
    3. LED lighting as a separate electrical measure.

    Gas and coal boiler savings are interpreted as post-insulation
    savings. This interpretation is supported by numerical
    consistency with the World Bank reference-school calculations,
    but the exact source calculation sequence is not explicitly
    confirmed.

    Fuel-switch options are excluded from calculated package
    savings because their complete energy balances are unresolved.
    """

    evaluation = evaluate_school(profile)

    climate_zone = profile["climate_zone"]
    school_area = profile["floor_area_m2"]
    heating_system = profile["heating_system"]

    baseline = calculate_baseline(
        climate_zone,
        school_area,
    )

    interventions = {
        item["intervention"]: item
        for item in evaluation["interventions"]
    }

    insulation = interventions["Insulation"]
    led = interventions["LED lighting"]

    if insulation["estimate_status"] != "estimated":
        raise ValueError(
            "Insulation savings are required for package evaluation."
        )

    if led["estimate_status"] != "estimated":
        raise ValueError(
            "LED savings are required for package evaluation."
        )

    insulation_saving = insulation[
        "estimated_energy_saving_kwh"
    ]

    heating_before = baseline["heating_kwh"]
    heating_after_insulation = (
        heating_before - insulation_saving
    )

    if heating_after_insulation < 0:
        raise ValueError(
            "Insulation savings exceed baseline heating demand."
        )

    selected_measures = [
        {
            "intervention": "Insulation",
            "energy_carrier": "thermal",
            "estimated_saving_kwh": insulation_saving,
            "investment_cost_usd_2021": (
                insulation["investment_cost_usd"]
            ),
        }
    ]

    boiler_saving = 0.0
    boiler_assumption = None

    boiler_name = SEQUENTIAL_BOILER_INTERVENTIONS.get(
        heating_system
    )

    if boiler_name is not None:
        boiler = interventions[boiler_name]

        if boiler["compatibility"] == "compatible":
            if boiler["estimate_status"] != "estimated":
                raise ValueError(
                    "The selected boiler saving is unresolved."
                )

            boiler_saving = boiler[
                "estimated_energy_saving_kwh"
            ]

            if boiler_saving > heating_after_insulation:
                raise ValueError(
                    "Boiler savings exceed post-insulation "
                    "heating demand."
                )

            selected_measures.append(
                {
                    "intervention": boiler_name,
                    "energy_carrier": "thermal",
                    "estimated_saving_kwh": boiler_saving,
                    "investment_cost_usd_2021": (
                        boiler["investment_cost_usd"]
                    ),
                }
            )

            boiler_assumption = (
                "The published boiler saving is treated as a "
                "post-insulation saving. This interpretation is "
                "supported by numerical consistency with the "
                "World Bank reference-school calculations, but "
                "the exact source calculation sequence is not "
                "explicitly confirmed."
            )

    led_saving = led["estimated_energy_saving_kwh"]

    selected_measures.append(
        {
            "intervention": "LED lighting",
            "energy_carrier": "electrical",
            "estimated_saving_kwh": led_saving,
            "investment_cost_usd_2021": (
                led["investment_cost_usd"]
            ),
        }
    )

    heating_after_package = (
        heating_after_insulation - boiler_saving
    )

    thermal_savings = insulation_saving + boiler_saving

    total_investment = sum(
        measure["investment_cost_usd_2021"]
        for measure in selected_measures
    )

    excluded_options = []

    for item in evaluation["interventions"]:
        if item["intervention"] in {
            "Coal-to-electric boiler",
            "Coal-to-air-to-water heat pump",
        }:
            excluded_options.append(
                {
                    "intervention": item["intervention"],
                    "reason": (
                        "Excluded from calculated package savings "
                        "because the complete energy balance and "
                        "additional electricity consumption are "
                        "not sufficiently documented."
                    ),
                }
            )

    return {
        "climate_zone": climate_zone,
        "school_area_m2": school_area,
        "heating_system": heating_system,
        "baseline_heating_kwh": heating_before,
        "heating_after_insulation_kwh": (
            heating_after_insulation
        ),
        "heating_after_package_kwh": heating_after_package,
        "thermal_savings_kwh": thermal_savings,
        "electrical_savings_kwh": led_saving,
        "total_investment_cost_usd_2021": total_investment,
        "selected_measures": selected_measures,
        "excluded_options": excluded_options,
        "boiler_assumption": boiler_assumption,
        "limitations": [
            (
                "Savings are estimates based on proportional "
                "floor-area scaling, not measured school results."
            ),
            (
                "Boiler savings are treated as post-insulation "
                "savings based on numerical consistency, not "
                "confirmed source methodology."
            ),
            (
                "Thermal and electrical savings are reported "
                "separately and are not added together."
            ),
            (
                "Investment costs are historical 2021 USD "
                "reference values and are not current quotations."
            ),
            (
                "Fuel-switch options are excluded until their "
                "complete energy balances are available."
            ),
        ],
    }
