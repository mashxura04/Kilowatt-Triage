import unittest

from src.evaluation import evaluate_school
from src.scaling import scale_interventions


HEATING_SYSTEMS = ["coal", "gas", "district", "electric", "other", "unknown"]


def make_profile(heating_system, area=4000):
    return {
        "climate_zone": 3,
        "floor_area_m2": area,
        "heating_system": heating_system,
        "heating_condition": "fair",
        "available_fuels": [],
        "electrical_capacity_kw": None,
    }


def find(results, name):
    return next(
        item
        for item in results["interventions"]
        if item["intervention"] == name
    )


class IncompatibleEstimateTests(unittest.TestCase):

    def test_gas_boiler_has_no_estimate_for_coal_school(self):
        results = evaluate_school(make_profile("coal"))
        gas_boiler = find(results, "Gas boiler retrofit")

        self.assertEqual(gas_boiler["compatibility"], "incompatible")
        self.assertIsNone(gas_boiler["estimated_energy_saving_kwh"])
        self.assertEqual(gas_boiler["estimate_status"], "not_applicable")
        self.assertIsNotNone(gas_boiler["estimate_limitation"])

    def test_compatible_coal_boiler_keeps_its_estimate(self):
        results = evaluate_school(make_profile("coal"))
        coal_boiler = find(results, "Efficient coal boiler")

        self.assertEqual(coal_boiler["compatibility"], "compatible")
        self.assertEqual(coal_boiler["estimated_energy_saving_kwh"], 188924)
        self.assertEqual(coal_boiler["estimate_status"], "estimated")

    def test_every_incompatible_measure_has_no_estimate(self):
        for system in HEATING_SYSTEMS:
            results = evaluate_school(make_profile(system))
            for item in results["interventions"]:
                if (
                    item["compatibility"] == "incompatible"
                    and item["reported_saving_basis"] != "fuel_switch_unresolved"
                ):
                    with self.subTest(
                        system=system, intervention=item["intervention"]
                    ):
                        self.assertIsNone(item["estimated_energy_saving_kwh"])
                        self.assertEqual(
                            item["estimate_status"], "not_applicable"
                        )

    def test_compatible_measures_still_have_numeric_estimates(self):
        for system in HEATING_SYSTEMS:
            results = evaluate_school(make_profile(system))
            for item in results["interventions"]:
                if (
                    item["compatibility"] == "compatible"
                    and item["reported_saving_basis"] != "fuel_switch_unresolved"
                ):
                    with self.subTest(
                        system=system, intervention=item["intervention"]
                    ):
                        self.assertEqual(item["estimate_status"], "estimated")
                        self.assertIsNotNone(
                            item["estimated_energy_saving_kwh"]
                        )

    def test_items_without_compatibility_field_are_unchanged(self):
        items = [
            {
                "intervention": "Example",
                "reported_energy_saving_kwh": 1000.0,
                "reported_saving_basis": "thermal",
            }
        ]

        result = scale_interventions(items, 2000)[0]

        self.assertEqual(result["estimated_energy_saving_kwh"], 500)
        self.assertEqual(result["estimate_status"], "estimated")


if __name__ == "__main__":
    unittest.main()