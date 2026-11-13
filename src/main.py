
from src.baseline import (
    REFERENCE_SCHOOL_AREA_M2,
    calculate_baseline,
    calculate_after_insulation,
)
from src.evaluation import evaluate_school
from src.package_evaluation import evaluate_retrofit_package
from src.school_profile import create_school_profile


SCHOOL_AREA_M2 = REFERENCE_SCHOOL_AREA_M2


SUPPLEMENTARY_DATA_FIELDS = {
    "Gas boiler retrofit": {
        "fuel_saved_m3": "Natural gas savings (m³)",
    },
    "Efficient coal boiler": {
        "fuel_saved_tonnes": "Coal savings (tonnes)",
    },
    "Coal-to-electric boiler": {
        "fuel_saved_tonnes": "Coal savings (tonnes)",
        "additional_electricity_kwh": (
            "Additional electricity consumption (kWh)"
        ),
    },
    "Coal-to-air-to-water heat pump": {
        "fuel_saved_tonnes": "Coal savings (tonnes)",
        "additional_electricity_kwh": (
            "Additional electricity consumption (kWh)"
        ),
    },
}


def get_school_profile():
    print("\n" + "=" * 60)
    print("SCHOOL INFORMATION")
    print("=" * 60)

    climate_zone = int(input("Climate zone (1-4): "))
    floor_area = float(input("School floor area (m²): "))

    print("\nHeating systems:")
    print("coal, gas, district, electric, other, unknown")

    heating_system = input(
        "Existing heating system: "
    ).strip().lower()

    print("\nHeating condition:")
    print("good, fair, poor, unknown")

    heating_condition = (
        input("Heating system condition (default: unknown): ")
        .strip()
        .lower()
        or "unknown"
    )

    print("\nAvailable fuels:")
    print("coal, natural_gas, electricity, other")
    print("Enter multiple fuels separated by commas.")
    print("Leave blank if unknown.")

    fuel_input = input("Available fuels: ").strip().lower()

    available_fuels = [
        fuel.strip()
        for fuel in fuel_input.split(",")
        if fuel.strip()
    ]

    capacity_input = input(
        "Electrical capacity in kW (leave blank if unknown): "
    ).strip()

    electrical_capacity = (
        float(capacity_input) if capacity_input else None
    )

    return create_school_profile(
        climate_zone=climate_zone,
        floor_area_m2=floor_area,
        heating_system=heating_system,
        heating_condition=heating_condition,
        available_fuels=available_fuels,
        electrical_capacity_kw=electrical_capacity,
    )


def display_school_baseline(profile):
    climate_zone = profile["climate_zone"]
    school_area = profile["floor_area_m2"]

    baseline = calculate_baseline(
        climate_zone,
        school_area,
    )

    print("\n" + "=" * 60)
    print("ESTIMATED ANNUAL ENERGY BASELINE")
    print("=" * 60)

    print(f"School area: {school_area:,.0f} m²")
    print(f"Climate zone: {climate_zone}")
    print(f"Reference school area: {SCHOOL_AREA_M2:,} m²")

    print("\nEstimated annual demand:")
    print(f"Heating (thermal): {baseline['heating_kwh']:,.0f} kWh")
    print(f"Lighting (electrical): {baseline['lighting_kwh']:,.0f} kWh")
    print(f"Equipment (electrical): {baseline['equipment_kwh']:,.0f} kWh")
    print(f"Total: {baseline['total_kwh']:,.0f} kWh")

    print("\nNote:")
    print(
        "Baseline values are scaled proportionally from the "
        "World Bank reference school."
    )
    print("They are estimates, not measured school consumption.")


def display_evaluation_report(profile, evaluation):
    print("\n" + "=" * 75)
    print("INDIVIDUAL INTERVENTION EVALUATION")
    print("=" * 75)

    print("\nSCHOOL PROFILE")
    print("-" * 75)

    print(f"Climate zone: {profile['climate_zone']}")
    print(f"Floor area: {profile['floor_area_m2']:,.0f} m²")
    print(f"Heating system: {profile['heating_system']}")
    print(f"Heating condition: {profile['heating_condition']}")

    fuels = profile["available_fuels"]

    print(
        "Available fuels: "
        + (", ".join(fuels) if fuels else "Unknown")
    )

    capacity = profile["electrical_capacity_kw"]

    print(
        "Electrical capacity: "
        + (
            f"{capacity:,.2f} kW"
            if capacity is not None
            else "Unknown"
        )
    )

    print("\nINTERVENTIONS")
    print("=" * 75)

    for index, item in enumerate(
        evaluation["interventions"],
        start=1,
    ):
        print(f"\n{index}. {item['intervention']}")
        print("-" * 75)

        if item["estimate_status"] == "unresolved":
            print(
                "World Bank reported figure: "
                f"{item['reported_energy_saving_kwh']:,.0f} kWh"
            )
            print("School-specific net energy saving: NOT CALCULATED")
            print(f"Reason: {item['estimate_limitation']}")

        elif item["estimate_status"] == "not_applicable":
            print(
                "World Bank reference-school figure: "
                f"{item['reported_energy_saving_kwh']:,.0f} kWh"
            )
            print("Estimated savings for this school: NOT APPLICABLE")
            print(f"Reason: {item['estimate_limitation']}")

        else:
            print(
                "World Bank reported savings: "
                f"{item['reported_energy_saving_kwh']:,.0f} kWh"
            )
            print(
                "Estimated savings for this school: "
                f"{item['estimated_energy_saving_kwh']:,.0f} kWh"
            )

        print(f"Savings category: {item['reported_saving_basis']}")
        print(f"Compatibility: {item['compatibility'].upper()}")
        print(f"Compatibility details: {item['compatibility_reason']}")

        print(
            "Reference investment cost (2021 USD): "
            f"${item['investment_cost_usd']:,.0f}"
        )

        print(f"Scaling assumption: {item['scaling_assumption']}")

        expected_data = SUPPLEMENTARY_DATA_FIELDS.get(
            item["intervention"],
            {},
        )

        missing_data = [
            description
            for field, description in expected_data.items()
            if item[field] is None
        ]

        if missing_data:
            print("\nSupplementary data not supplied:")

            for description in missing_data:
                print(f"- {description}")

        if item["estimate_status"] == "unresolved":
            print(
                "Calculation status: Net school-specific savings "
                "cannot be determined from the available data."
            )


def display_package_report(profile):
    package = evaluate_retrofit_package(profile)

    print("\n" + "=" * 75)
    print("KILOWATT TRIAGE - RETROFIT PACKAGE")
    print("=" * 75)

    print("\nSELECTED MEASURES")

    for index, measure in enumerate(
        package["selected_measures"],
        start=1,
    ):
        print(f"\n{index}. {measure['intervention']}")
        print(f"   Energy carrier: {measure['energy_carrier']}")
        print(
            "   Estimated savings: "
            f"{measure['estimated_saving_kwh']:,.0f} kWh"
        )
        print(
            "   Reference investment cost: "
            f"${measure['investment_cost_usd_2021']:,.0f}"
        )

    print("\n" + "-" * 75)
    print("HEATING SYSTEM RESULTS")
    print("-" * 75)

    print(
        "Baseline heating demand: "
        f"{package['baseline_heating_kwh']:,.0f} kWh"
    )

    print(
        "After insulation: "
        f"{package['heating_after_insulation_kwh']:,.0f} kWh"
    )

    print(
        "After selected heating measures: "
        f"{package['heating_after_package_kwh']:,.0f} kWh"
    )

    print(
        "Estimated thermal savings: "
        f"{package['thermal_savings_kwh']:,.0f} kWh"
    )

    print("\nELECTRICAL SAVINGS")
    print("-" * 75)

    print(
        "Estimated LED electricity savings: "
        f"{package['electrical_savings_kwh']:,.0f} kWh"
    )

    print(
        "\nThermal and electrical savings are reported separately. "
        "They are not combined into one total."
    )

    print("\nINVESTMENT")
    print("-" * 75)

    print(
        "Sum of reference investment costs: "
        f"${package['total_investment_cost_usd_2021']:,.0f}"
    )

    print(
        "These are historical 2021 USD reference costs, not "
        "current quotations or a verified school-specific budget."
    )

    if package["boiler_assumption"]:
        print("\nSEQUENTIAL BOILER ASSUMPTION")
        print("-" * 75)
        print(package["boiler_assumption"])

    print("\nEXCLUDED OPTIONS")
    print("-" * 75)

    if package["excluded_options"]:
        for option in package["excluded_options"]:
            print(f"- {option['intervention']}")
            print(f"  Reason: {option['reason']}")
    else:
        print("No fuel-switch options were listed.")

    print("\nPACKAGE LIMITATIONS")
    print("-" * 75)

    for limitation in package["limitations"]:
        print(f"- {limitation}")


def main():
    print("\n" + "=" * 60)
    print("WELCOME TO KILOWATT TRIAGE")
    print("School Energy Retrofit Decision-Support Prototype")
    print("=" * 60)

    try:
        profile = get_school_profile()
        evaluation = evaluate_school(profile)

        display_school_baseline(profile)
        display_evaluation_report(profile, evaluation)
        display_package_report(profile)

        print("\n" + "=" * 60)
        print("END OF REPORT")
        print("=" * 60)

    except (ValueError, KeyError) as error:
        print(f"\nInput or evaluation error: {error}")


if __name__ == "__main__":
    main()