import unittest

from src.package_evaluation import evaluate_retrofit_package
from src.school_profile import create_school_profile


class TestRetrofitPackageEvaluation(unittest.TestCase):

    def make_profile(
        self,
        heating_system="coal",
        floor_area_m2=4000,
    ):
        return create_school_profile(
            climate_zone=3,
            floor_area_m2=floor_area_m2,
            heating_system=heating_system,
            available_fuels=[],
            electrical_capacity_kw=None,
        )

    def find_measure(self, package, name):
        for item in package["selected_measures"]:
            if item["intervention"] == name:
                return item

        self.fail(f"Selected measure not found: {name}")

    def test_package_includes_insulation_and_led(self):
        package = evaluate_retrofit_package(self.make_profile())

        selected = [
            item["intervention"]
            for item in package["selected_measures"]
        ]

        self.assertIn("Insulation", selected)
        self.assertIn("LED lighting", selected)

    def test_coal_school_gets_compatible_boiler_upgrade(self):
        package = evaluate_retrofit_package(self.make_profile())

        selected = [
            item["intervention"]
            for item in package["selected_measures"]
        ]

        self.assertIn("Efficient coal boiler", selected)

    def test_thermal_and_electrical_savings_are_separate(self):
        package = evaluate_retrofit_package(self.make_profile())

        self.assertGreater(package["thermal_savings_kwh"], 0)
        self.assertGreater(package["electrical_savings_kwh"], 0)

    def test_thermal_savings_equal_insulation_plus_boiler(self):
        package = evaluate_retrofit_package(self.make_profile())

        insulation = self.find_measure(package, "Insulation")
        boiler = self.find_measure(package, "Efficient coal boiler")

        expected = (
            insulation["estimated_saving_kwh"]
            + boiler["estimated_saving_kwh"]
        )

        self.assertAlmostEqual(
            package["thermal_savings_kwh"],
            expected,
        )

    def test_investment_cost_equals_selected_measure_costs(self):
        package = evaluate_retrofit_package(self.make_profile())

        expected = sum(
            item["investment_cost_usd_2021"]
            for item in package["selected_measures"]
        )

        self.assertAlmostEqual(
            package["total_investment_cost_usd_2021"],
            expected,
        )

    def test_investment_cost_basis_is_disclosed(self):
        package = evaluate_retrofit_package(self.make_profile())

        self.assertIn(
            "not adjusted",
            package["investment_cost_basis"],
        )

    def test_fuel_switch_options_are_excluded(self):
        package = evaluate_retrofit_package(self.make_profile())

        excluded = [
            item["intervention"]
            for item in package["excluded_options"]
        ]

        self.assertIn("Coal-to-electric boiler", excluded)
        self.assertIn("Coal-to-air-to-water heat pump", excluded)

    def test_package_includes_methodological_limitations(self):
        package = evaluate_retrofit_package(self.make_profile())

        self.assertGreaterEqual(len(package["limitations"]), 5)

        for limitation in package["limitations"]:
            self.assertIsInstance(limitation, str)
            self.assertTrue(limitation.strip())


if __name__ == "__main__":
    unittest.main()