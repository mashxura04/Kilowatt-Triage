
from src.compatibility import evaluate_interventions
from src.data_loader import get_interventions_by_zone
from src.scaling import scale_interventions
from src.school_profile import create_school_profile


ELECTRICAL_CONVERSION_OPTIONS = {
    "Coal-to-electric boiler",
    "Coal-to-air-to-water heat pump",
}


def validate_evaluation_profile(profile):
    """
    Validate a school profile before evaluation.

    Reuses create_school_profile so that the evaluation module
    follows the same validation rules as the profile module.
    """

    if not isinstance(profile, dict):
        raise ValueError("School profile must be a dictionary.")

    required_fields = {
        "climate_zone",
        "floor_area_m2",
        "heating_system",
        "heating_condition",
        "available_fuels",
        "electrical_capacity_kw",
    }

    missing_fields = required_fields - set(profile)

    if missing_fields:
        raise ValueError(
            f"School profile is missing fields: {sorted(missing_fields)}"
        )

    validated_profile = create_school_profile(
        climate_zone=profile["climate_zone"],
        floor_area_m2=profile["floor_area_m2"],
        heating_system=profile["heating_system"],
        heating_condition=profile["heating_condition"],
        available_fuels=profile["available_fuels"],
        electrical_capacity_kw=profile["electrical_capacity_kw"],
    )

    return validated_profile


def evaluate_school(profile):
    """
    Evaluate interventions against a school's recorded profile.

    Reported World Bank savings are adjusted proportionally
    to the school's floor area.

    Scaled savings are estimates, not measured results.
    Investment costs are not scaled.
    """

    validated_profile = validate_evaluation_profile(profile)

    climate_zone = validated_profile["climate_zone"]
    heating_system = validated_profile["heating_system"]
    floor_area_m2 = validated_profile["floor_area_m2"]

    interventions = get_interventions_by_zone(climate_zone)

    results = evaluate_interventions(
        interventions,
        heating_system,
    )

    # Preserve the general compatibility decision while providing
    # school-specific explanations for electrical conversions.
    for item in results:
        if (
            item["intervention"] in ELECTRICAL_CONVERSION_OPTIONS
            and item["compatibility"] == "needs_review"
            and heating_system == "coal"
        ):
            electricity_available = (
                "electricity" in validated_profile["available_fuels"]
            )

            capacity_known = (
                validated_profile["electrical_capacity_kw"] is not None
            )

            if not electricity_available:
                item["compatibility_reason"] = (
                    "Electrical conversion requires confirmation that "
                    "electricity is available to the school."
                )

            elif not capacity_known:
                item["compatibility_reason"] = (
                    "Electricity is listed as available, but the school's "
                    "electrical capacity is unknown."
                )

            else:
                item["compatibility_reason"] = (
                    "Electricity is listed as available and capacity "
                    "information is recorded. The required electrical "
                    "load must still be assessed before determining "
                    "suitability."
                )

    scaled_results = scale_interventions(
        results,
        floor_area_m2,
    )

    # Keep any additional profile information, but make sure the
    # nested fuel list is independent of the original profile.
    profile_copy = profile.copy()
    profile_copy["available_fuels"] = (
        validated_profile["available_fuels"].copy()
    )

    return {
        "school_profile": profile_copy,
        "climate_zone": climate_zone,
        "interventions": scaled_results,
    }


def evaluate_school_interventions(profile):
    """
    Backward-compatible interface.

    Returns the evaluated intervention list rather than
    the complete evaluation report.
    """

    results = evaluate_school(profile)

    return results["interventions"]
