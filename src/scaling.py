import math


REFERENCE_SCHOOL_AREA_M2 = 4000

VALID_BASES = {
    "thermal",
    "electrical",
    "fuel_switch_unresolved",
}

UNRESOLVED_BASES = {
    "fuel_switch_unresolved",
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


def validate_nonnegative_finite_number(value, field_name):
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or value < 0
    ):
        raise ValueError(
            f"{field_name} must be a finite non-negative number."
        )


def calculate_scaling_factor(
    school_area_m2,
    reference_area_m2=REFERENCE_SCHOOL_AREA_M2,
):
    validate_positive_finite_number(
        school_area_m2,
        "School area",
    )

    validate_positive_finite_number(
        reference_area_m2,
        "Reference area",
    )

    return school_area_m2 / reference_area_m2


def scale_energy_value(
    value,
    school_area_m2,
    reference_area_m2=REFERENCE_SCHOOL_AREA_M2,
):
    validate_nonnegative_finite_number(
        value,
        "Energy value",
    )

    factor = calculate_scaling_factor(
        school_area_m2,
        reference_area_m2,
    )

    return value * factor


def scale_interventions(
    interventions,
    school_area_m2,
    reference_area_m2=REFERENCE_SCHOOL_AREA_M2,
):
    factor = calculate_scaling_factor(
        school_area_m2,
        reference_area_m2,
    )

    scaled_results = []

    for intervention in interventions:
        scaled_intervention = intervention.copy()

        original_saving = intervention["reported_energy_saving_kwh"]
        saving_basis = intervention.get("reported_saving_basis")

        validate_nonnegative_finite_number(
            original_saving,
            "Reported energy saving",
        )

        if saving_basis not in VALID_BASES:
            raise ValueError(
                f"Invalid or missing savings basis: {saving_basis!r}. "
                f"Expected one of: {sorted(VALID_BASES)}."
            )

        scaled_intervention["scaling_factor"] = factor

        if saving_basis in UNRESOLVED_BASES:
            scaled_intervention["estimated_energy_saving_kwh"] = None

            scaled_intervention["estimate_status"] = "unresolved"

            scaled_intervention["estimate_limitation"] = (
                "A school-specific net energy saving cannot be calculated "
                "because the additional electricity consumption and "
                "complete energy balance are unavailable."
            )

            scaled_intervention["scaling_assumption"] = (
                "The World Bank reported figure is preserved, but it is "
                "not scaled or presented as a school-specific net saving."
            )

        elif intervention.get("compatibility") == "incompatible":
            # The measure does not fit this school's heating system, so
            # no school-specific saving is estimated. The reported figure
            # remains visible but describes the reference school only.
            scaled_intervention["estimated_energy_saving_kwh"] = None

            scaled_intervention["estimate_status"] = "not_applicable"

            scaled_intervention["estimate_limitation"] = (
                "No saving is estimated because this intervention is "
                "incompatible with the school's recorded heating system."
            )

            scaled_intervention["scaling_assumption"] = (
                "Not scaled. The World Bank reported figure describes "
                "the reference school and does not apply to this school."
            )

        else:
            scaled_intervention["estimated_energy_saving_kwh"] = (
                scale_energy_value(
                    original_saving,
                    school_area_m2,
                    reference_area_m2,
                )
            )

            scaled_intervention["estimate_status"] = "estimated"

            scaled_intervention["estimate_limitation"] = None

            scaled_intervention["scaling_assumption"] = (
                "Energy savings are assumed to scale proportionally "
                "with floor area. This is an estimate, not a measured result."
            )

        scaled_results.append(scaled_intervention)

    return scaled_results