
VALID_HEATING_SYSTEMS = {
    "coal",
    "gas",
    "district",
    "electric",
    "other",
    "unknown",
}

GENERAL_INTERVENTIONS = {
    "Insulation",
    "LED lighting",
}

HEATING_REQUIREMENTS = {
    "Gas boiler retrofit": "gas",
    "Efficient coal boiler": "coal",
    "Coal-to-electric boiler": "coal",
    "Coal-to-air-to-water heat pump": "coal",
}

FUEL_SWITCH_INTERVENTIONS = {
    "Coal-to-electric boiler",
    "Coal-to-air-to-water heat pump",
}


def validate_heating_system(heating_system):
    if (
        not isinstance(heating_system, str)
        or heating_system not in VALID_HEATING_SYSTEMS
    ):
        raise ValueError("Invalid heating system.")


def validate_intervention_name(intervention):
    if not isinstance(intervention, str):
        raise ValueError("Intervention name must be a string.")

    if (
        intervention not in GENERAL_INTERVENTIONS
        and intervention not in HEATING_REQUIREMENTS
    ):
        raise ValueError(f"Unknown intervention: {intervention}")


def check_compatibility(intervention, heating_system):
    validate_heating_system(heating_system)
    validate_intervention_name(intervention)

    if intervention in GENERAL_INTERVENTIONS:
        return {
            "status": "compatible",
            "reason": "This intervention does not depend on the heating fuel.",
        }

    required_system = HEATING_REQUIREMENTS[intervention]

    if heating_system == "unknown":
        return {
            "status": "needs_review",
            "reason": "The school's heating system is unknown.",
        }

    if heating_system in {"district", "electric", "other"}:
        return {
            "status": "needs_review",
            "reason": (
                "The existing heating system does not match the "
                "modelled retrofit case. Further technical review is needed."
            ),
        }

    if heating_system != required_system:
        return {
            "status": "incompatible",
            "reason": (
                f"This intervention requires a {required_system}-based "
                f"heating system, but the school uses {heating_system}."
            ),
        }

    if intervention in FUEL_SWITCH_INTERVENTIONS:
        return {
            "status": "needs_review",
            "reason": (
                "The school uses coal heating, but conversion requires "
                "assessment of electrical capacity, infrastructure, "
                "and technical suitability."
            ),
        }

    return {
        "status": "compatible",
        "reason": (
            f"This intervention matches the school's "
            f"{heating_system}-based heating system."
        ),
    }


def evaluate_interventions(interventions, heating_system):
    validate_heating_system(heating_system)

    results = []

    for intervention in interventions:
        if not isinstance(intervention, dict):
            raise ValueError("Each intervention must be a dictionary.")

        if "intervention" not in intervention:
            raise ValueError(
                "Each intervention must contain an intervention name."
            )

        result = check_compatibility(
            intervention["intervention"],
            heating_system,
        )

        evaluated_intervention = intervention.copy()
        evaluated_intervention["compatibility"] = result["status"]
        evaluated_intervention["compatibility_reason"] = result["reason"]

        results.append(evaluated_intervention)

    return results
