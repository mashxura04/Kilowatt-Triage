
import unittest
from copy import deepcopy

from src.scaling import (
    calculate_scaling_factor,
    scale_energy_value,
    scale_interventions,
)


class TestScaling(unittest.TestCase):

    def test_reference_school_factor_is_one(self):
        factor = calculate_scaling_factor(4000)
        self.assertEqual(factor, 1.0)

    def test_half_size_school_factor(self):
        factor = calculate_scaling_factor(2000)
        self.assertEqual(factor, 0.5)

    def test_double_size_school_factor(self):
        factor = calculate_scaling_factor(8000)
        self.assertEqual(factor, 2.0)

    def test_energy_value_is_scaled(self):
        result = scale_energy_value(100000, 2000)
        self.assertEqual(result, 50000)

    def test_reference_area_preserves_original_value(self):
        result = scale_energy_value(392482, 4000)
        self.assertEqual(result, 392482)

    def test_invalid_school_area_is_rejected(self):
        for area in [0, -100]:
            with self.subTest(area=area):
                with self.assertRaises(ValueError):
                    calculate_scaling_factor(area)

    def test_invalid_reference_area_is_rejected(self):
        for area in [0, -100]:
            with self.subTest(area=area):
                with self.assertRaises(ValueError):
                    calculate_scaling_factor(2000, area)

    def test_negative_energy_value_is_rejected(self):
        with self.assertRaises(ValueError):
            scale_energy_value(-100, 2000)

    def test_intervention_savings_are_scaled(self):
        interventions = [
            {
                "intervention": "Insulation",
                "reported_energy_saving_kwh": 392482,
                "reported_saving_basis": "thermal",
                "investment_cost_usd": 33043,
            }
        ]

        results = scale_interventions(interventions, 2000)

        self.assertEqual(
            results[0]["estimated_energy_saving_kwh"],
            196241,
        )

        self.assertEqual(results[0]["estimate_status"], "estimated")

    def test_reference_school_interventions_remain_unchanged(self):
        interventions = [
            {
                "intervention": "LED lighting",
                "reported_energy_saving_kwh": 14638,
                "reported_saving_basis": "electrical",
                "investment_cost_usd": 815,
            }
        ]

        results = scale_interventions(interventions, 4000)

        self.assertEqual(
            results[0]["estimated_energy_saving_kwh"],
            14638,
        )

    def test_original_interventions_are_not_modified(self):
        interventions = [
            {
                "intervention": "Insulation",
                "reported_energy_saving_kwh": 392482,
                "reported_saving_basis": "thermal",
                "investment_cost_usd": 33043,
            }
        ]

        original = deepcopy(interventions)

        scale_interventions(interventions, 2000)

        self.assertEqual(interventions, original)

    def test_investment_cost_is_not_scaled(self):
        interventions = [
            {
                "intervention": "Insulation",
                "reported_energy_saving_kwh": 392482,
                "reported_saving_basis": "thermal",
                "investment_cost_usd": 33043,
            }
        ]

        results = scale_interventions(interventions, 2000)

        self.assertEqual(
            results[0]["investment_cost_usd"],
            33043,
        )

    def test_unresolved_fuel_switch_is_not_scaled(self):
        interventions = [
            {
                "intervention": "Coal-to-electric boiler",
                "reported_energy_saving_kwh": 195350,
                "reported_saving_basis": "fuel_switch_unresolved",
                "investment_cost_usd": 10400,
            }
        ]

        results = scale_interventions(interventions, 2000)
        result = results[0]

        self.assertIsNone(
            result["estimated_energy_saving_kwh"]
        )

        self.assertEqual(
            result["estimate_status"],
            "unresolved",
        )

        self.assertEqual(
            result["reported_energy_saving_kwh"],
            195350,
        )

        self.assertEqual(
            result["scaling_factor"],
            0.5,
        )

    def test_unresolved_estimate_explains_missing_energy_balance(self):
        interventions = [
            {
                "intervention": "Coal-to-electric boiler",
                "reported_energy_saving_kwh": 195350,
                "reported_saving_basis": "fuel_switch_unresolved",
                "investment_cost_usd": 10400,
            }
        ]

        results = scale_interventions(interventions, 2000)

        limitation = results[0]["estimate_limitation"]

        self.assertIsNotNone(limitation)
        self.assertIn("additional electricity", limitation)
        self.assertIn("energy balance", limitation)

    def test_unresolved_estimate_discloses_scaling_assumption(self):
        interventions = [
            {
                "intervention": "Coal-to-electric boiler",
                "reported_energy_saving_kwh": 195350,
                "reported_saving_basis": "fuel_switch_unresolved",
                "investment_cost_usd": 10400,
            }
        ]

        results = scale_interventions(interventions, 2000)

        self.assertIn(
            "not scaled",
            results[0]["scaling_assumption"],
        )

    def test_unresolved_input_interventions_are_not_modified(self):
        interventions = [
            {
                "intervention": "Coal-to-electric boiler",
                "reported_energy_saving_kwh": 195350,
                "reported_saving_basis": "fuel_switch_unresolved",
                "investment_cost_usd": 10400,
            }
        ]

        original = deepcopy(interventions)

        scale_interventions(interventions, 2000)

        self.assertEqual(interventions, original)

    def test_electrical_savings_are_scaled(self):
        interventions = [
            {
                "intervention": "LED lighting",
                "reported_energy_saving_kwh": 14638,
                "reported_saving_basis": "electrical",
                "investment_cost_usd": 815,
            }
        ]

        results = scale_interventions(interventions, 2000)

        self.assertEqual(
            results[0]["estimated_energy_saving_kwh"],
            7319,
        )

        self.assertEqual(
            results[0]["estimate_status"],
            "estimated",
        )

        self.assertIsNone(
            results[0]["estimate_limitation"]
        )

    def test_custom_reference_area(self):
        factor = calculate_scaling_factor(
            school_area_m2=2000,
            reference_area_m2=2000,
        )

        self.assertEqual(factor, 1.0)

    def test_custom_reference_area_scales_energy_correctly(self):
        result = scale_energy_value(
            value=100000,
            school_area_m2=3000,
            reference_area_m2=6000,
        )

        self.assertEqual(result, 50000)

    def test_scale_interventions_rejects_invalid_school_area(self):
        interventions = []

        for area in [0, -100]:
            with self.subTest(area=area):
                with self.assertRaises(ValueError):
                    scale_interventions(interventions, area)

    def test_scale_interventions_rejects_invalid_reference_area(self):
        interventions = []

        for area in [0, -100]:
            with self.subTest(area=area):
                with self.assertRaises(ValueError):
                    scale_interventions(
                        interventions,
                        school_area_m2=2000,
                        reference_area_m2=area,
                    )

    def test_missing_savings_basis_is_rejected(self):
        interventions = [
            {
                "intervention": "Insulation",
                "reported_energy_saving_kwh": 392482,
                "investment_cost_usd": 33043,
            }
        ]

        with self.assertRaises(ValueError):
            scale_interventions(interventions, 2000)

    def test_unknown_savings_basis_is_rejected(self):
        interventions = [
            {
                "intervention": "Insulation",
                "reported_energy_saving_kwh": 392482,
                "reported_saving_basis": "therml",
                "investment_cost_usd": 33043,
            }
        ]

        with self.assertRaises(ValueError):
            scale_interventions(interventions, 2000)

    # Additional numeric validation tests

    def test_nonfinite_school_areas_are_rejected(self):
        for area in [float("nan"), float("inf"), float("-inf")]:
            with self.subTest(area=area):
                with self.assertRaises(ValueError):
                    calculate_scaling_factor(area)

    def test_nonfinite_reference_areas_are_rejected(self):
        for area in [float("nan"), float("inf"), float("-inf")]:
            with self.subTest(area=area):
                with self.assertRaises(ValueError):
                    calculate_scaling_factor(2000, area)

    def test_boolean_areas_are_rejected(self):
        for area in [True, False]:
            with self.subTest(area=area):
                with self.assertRaises(ValueError):
                    calculate_scaling_factor(area)

    def test_non_numeric_areas_are_rejected(self):
        for area in ["2000", None, []]:
            with self.subTest(area=area):
                with self.assertRaises(ValueError):
                    calculate_scaling_factor(area)

    def test_nonfinite_energy_values_are_rejected(self):
        for value in [float("nan"), float("inf"), float("-inf")]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    scale_energy_value(value, 2000)

    def test_boolean_energy_values_are_rejected(self):
        for value in [True, False]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    scale_energy_value(value, 2000)

    def test_non_numeric_energy_values_are_rejected(self):
        for value in ["1000", None, []]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    scale_energy_value(value, 2000)

    def test_nonfinite_intervention_savings_are_rejected(self):
        for value in [float("nan"), float("inf"), float("-inf")]:
            with self.subTest(value=value):
                interventions = [
                    {
                        "intervention": "Insulation",
                        "reported_energy_saving_kwh": value,
                        "reported_saving_basis": "thermal",
                    }
                ]

                with self.assertRaises(ValueError):
                    scale_interventions(interventions, 2000)

    def test_negative_intervention_savings_are_rejected(self):
        interventions = [
            {
                "intervention": "Insulation",
                "reported_energy_saving_kwh": -1,
                "reported_saving_basis": "thermal",
            }
        ]

        with self.assertRaises(ValueError):
            scale_interventions(interventions, 2000)


if __name__ == "__main__":
    unittest.main()
