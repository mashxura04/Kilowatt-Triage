
import unittest

from src.budget_optimizer import (
    optimize_retrofit_budget,
    validate_budget,
)
from src.school_profile import create_school_profile


class TestBudgetOptimizer(unittest.TestCase):

    def setUp(self):
        self.profile = create_school_profile(
            climate_zone=3,
            floor_area_m2=4000,
            heating_system="coal",
            available_fuels=[],
            electrical_capacity_kw=None,
        )

    def test_rejects_negative_budget(self):
        with self.assertRaises(ValueError):
            validate_budget(-1)

    def test_rejects_invalid_budget(self):
        for budget in ["1000", None, float("inf"), float("nan")]:
            with self.subTest(budget=budget):
                with self.assertRaises(ValueError):
                    validate_budget(budget)

    def test_never_exceeds_budget(self):
        result = optimize_retrofit_budget(self.profile, 40000)

        for scenario in (
            result["thermal_optimization"],
            result["electrical_optimization"],
        ):
            self.assertLessEqual(
                scenario["investment_cost_usd_2021"],
                40000,
            )

    def test_thermal_package_preserves_insulation_dependency(self):
        result = optimize_retrofit_budget(self.profile, 50000)

        selected = result["thermal_optimization"]["selected_measures"]
        names = [item["intervention"] for item in selected]

        if "Efficient coal boiler" in names:
            self.assertIn("Insulation", names)

    def test_thermal_and_electrical_savings_are_separate(self):
        result = optimize_retrofit_budget(self.profile, 50000)

        thermal = result["thermal_optimization"]
        electrical = result["electrical_optimization"]

        self.assertNotEqual(
            thermal["estimated_savings_kwh"],
            electrical["estimated_savings_kwh"],
        )

    def test_electrical_option_is_led(self):
        result = optimize_retrofit_budget(self.profile, 50000)

        selected = result["electrical_optimization"]["selected_measures"]
        names = [item["intervention"] for item in selected]

        self.assertTrue(
            all(name == "LED lighting" for name in names)
        )

    def test_zero_budget_selects_no_measures(self):
        result = optimize_retrofit_budget(self.profile, 0)

        for scenario in (
            result["thermal_optimization"],
            result["electrical_optimization"],
        ):
            self.assertEqual(scenario["selected_measures"], [])
            self.assertEqual(
                scenario["investment_cost_usd_2021"],
                0,
            )

    def test_33043_budget_selects_insulation_only(self):
        result = optimize_retrofit_budget(self.profile, 33043)
        thermal = result["thermal_optimization"]

        self.assertEqual(
            [m["intervention"] for m in thermal["selected_measures"]],
            ["Insulation"],
        )
        self.assertEqual(thermal["estimated_savings_kwh"], 392482)

    def test_50000_budget_selects_insulation_and_coal_boiler(self):
        result = optimize_retrofit_budget(self.profile, 50000)
        thermal = result["thermal_optimization"]

        self.assertEqual(
            [m["intervention"] for m in thermal["selected_measures"]],
            ["Insulation", "Efficient coal boiler"],
        )
        self.assertEqual(thermal["estimated_savings_kwh"], 581406)
        self.assertEqual(thermal["investment_cost_usd_2021"], 46543)

    def test_815_budget_selects_led_only_in_electrical_scenario(self):
        result = optimize_retrofit_budget(self.profile, 815)

        self.assertEqual(
            result["thermal_optimization"]["selected_measures"],
            [],
        )
        self.assertEqual(
            [
                m["intervention"]
                for m in result["electrical_optimization"]["selected_measures"]
            ],
            ["LED lighting"],
        )


if __name__ == "__main__":
    unittest.main()
