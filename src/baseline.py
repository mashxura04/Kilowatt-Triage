import math

from src.data_loader import get_interventions_by_zone


REFERENCE_SCHOOL_AREA_M2 = 4000

CLIMATE_ZONES = {
    1: {
        "heating": 118.14,
        "lighting": 5.63,
        "equipment": 1.75,
    },
    2: {
        "heating": 178.94,
        "lighting": 5.63,
        "equipment": 1.75,
    },
    3: {
        "heating": 224.07,
        "lighting": 5.63,
        "equipment": 1.75,
    },
    4: {
        "heating": 230.05,
        "lighting": 5.63,
        "equipment": 1.75,
    },
}


def validate_school_area(school_area_m2):
    if (
        isinstance(school_area_m2, bool)
        or not isinstance(school_area_m2, (int, float))
        or not math.isfinite(school_area_m2)
        or school_area_m2 <= 0
    ):
        raise ValueError(
            "School area must be a finite number greater than zero."
        )


def validate_climate_zone(climate_zone):
    if (
        isinstance(climate_zone, bool)
        or climate_zone not in CLIMATE_ZONES
    ):
        raise ValueError("Climate zone must be between 1 and 4.")


def calculate_baseline(
    climate_zone,
    school_area_m2=REFERENCE_SCHOOL_AREA_M2,
):
    validate_climate_zone(climate_zone)
    validate_school_area(school_area_m2)

    zone_data = CLIMATE_ZONES[climate_zone]

    heating = zone_data["heating"] * school_area_m2
    lighting = zone_data["lighting"] * school_area_m2
    equipment = zone_data["equipment"] * school_area_m2

    return {
        "heating_kwh": heating,
        "lighting_kwh": lighting,
        "equipment_kwh": equipment,
        "total_kwh": heating + lighting + equipment,
    }


def calculate_after_insulation(
    climate_zone,
    school_area_m2=REFERENCE_SCHOOL_AREA_M2,
):
    baseline = calculate_baseline(
        climate_zone,
        school_area_m2,
    )

    interventions = get_interventions_by_zone(climate_zone)

    insulation_records = [
        item for item in interventions
        if item["intervention"] == "Insulation"
    ]

    if len(insulation_records) != 1:
        raise ValueError(
            "Expected exactly one insulation record "
            f"for climate zone {climate_zone}."
        )

    insulation = insulation_records[0]

    if insulation.get("reported_saving_basis") != "thermal":
        raise ValueError(
            "Insulation savings must be classified as thermal "
            "before they can be subtracted from heating demand."
        )

    reported_saving = insulation["reported_energy_saving_kwh"]

    if (
        isinstance(reported_saving, bool)
        or not isinstance(reported_saving, (int, float))
        or not math.isfinite(reported_saving)
        or reported_saving < 0
    ):
        raise ValueError(
            "Reported insulation savings must be a finite "
            "non-negative number."
        )

    scaling_factor = (
        school_area_m2 / REFERENCE_SCHOOL_AREA_M2
    )

    heating_before = baseline["heating_kwh"]

    heating_saved = reported_saving * scaling_factor

    heating_after = heating_before - heating_saved

    if heating_after < 0:
        raise ValueError(
            "Insulation savings exceed baseline heating demand."
        )

    return {
        "heating_before_kwh": heating_before,
        "heating_saved_kwh": heating_saved,
        "heating_after_kwh": heating_after,
        "saving_percentage": (
            heating_saved / heating_before * 100
        ),
    }