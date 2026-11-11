
import math


VALID_CLIMATE_ZONES = {1, 2, 3, 4}

VALID_HEATING_SYSTEMS = {
    "coal",
    "gas",
    "district",
    "electric",
    "other",
    "unknown",
}

VALID_HEATING_CONDITIONS = {
    "good",
    "fair",
    "poor",
    "unknown",
}

VALID_FUELS = {
    "coal",
    "natural_gas",
    "electricity",
    "other",
}


def validate_positive_finite_number(value, field_name):
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or value <= 0
    ):
        raise ValueError(
            f"{field_name} must be a finite number greater than zero."
        )


def create_school_profile(
    climate_zone,
    floor_area_m2,
    heating_system,
    heating_condition="unknown",
    available_fuels=None,
    electrical_capacity_kw=None,
):
    if (
        isinstance(climate_zone, bool)
        or not isinstance(climate_zone, int)
        or climate_zone not in VALID_CLIMATE_ZONES
    ):
        raise ValueError("Climate zone must be an integer between 1 and 4.")

    validate_positive_finite_number(
        floor_area_m2,
        "Floor area",
    )

    if (
        not isinstance(heating_system, str)
        or heating_system not in VALID_HEATING_SYSTEMS
    ):
        raise ValueError("Invalid heating system.")

    if (
        not isinstance(heating_condition, str)
        or heating_condition not in VALID_HEATING_CONDITIONS
    ):
        raise ValueError("Invalid heating system condition.")

    if available_fuels is None:
        available_fuels = []

    if not isinstance(available_fuels, list):
        raise ValueError("Available fuels must be provided as a list.")

    if any(
        not isinstance(fuel, str) or fuel not in VALID_FUELS
        for fuel in available_fuels
    ):
        raise ValueError("One or more available fuels are invalid.")

    if electrical_capacity_kw is not None:
        validate_positive_finite_number(
            electrical_capacity_kw,
            "Electrical capacity",
        )

    return {
        "climate_zone": climate_zone,
        "floor_area_m2": floor_area_m2,
        "heating_system": heating_system,
        "heating_condition": heating_condition,
        "available_fuels": available_fuels.copy(),
        "electrical_capacity_kw": electrical_capacity_kw,
    }
