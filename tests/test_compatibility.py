
import unittest

from src.compatibility import (
    check_compatibility,
    evaluate_interventions,
)


class TestCompatibility(unittest.TestCase):

    def test_insulation_is_compatible_with_all_heating_systems(self):
        systems = [
            "coal", "gas", "district", "electric", "other", "unknown"
        ]

        for system in systems:
            with self.subTest(system=system):
                result = check_compatibility("Insulation", system)
                self.assertEqual(result["status"], "compatible")

    def test_led_is_compatible_with_all_heating_systems(self):
        systems = [
            "coal", "gas", "district", "electric", "other", "unknown"
        ]

        for system in systems:
            with self.subTest(system=system):
                result = check_compatibility("LED lighting", system)
                self.assertEqual(result["status"], "compatible")

    def test_gas_boiler_matches_gas_heating(self):
        result = check_compatibility("Gas boiler retrofit", "gas")
        self.assertEqual(result["status"], "compatible")

    def test_coal_boiler_matches_coal_heating(self):
        result = check_compatibility("Efficient coal boiler", "coal")
        self.assertEqual(result["status"], "compatible")

    def test_coal_conversion_options_need_technical_review(self):
        interventions = [
            "Coal-to-electric boiler",
            "Coal-to-air-to-water heat pump",
        ]

        for intervention in interventions:
            with self.subTest(intervention=intervention):
                result = check_compatibility(intervention, "coal")
                self.assertEqual(result["status"], "needs_review")

    def test_coal_conversion_review_explains_technical_requirements(self):
        interventions = [
            "Coal-to-electric boiler",
            "Coal-to-air-to-water heat pump",
        ]

        for intervention in interventions:
            with self.subTest(intervention=intervention):
                result = check_compatibility(intervention, "coal")

                self.assertIn("electrical capacity", result["reason"])
                self.assertIn("technical suitability", result["reason"])

    def test_coal_conversion_is_incompatible_with_gas_heating(self):
        interventions = [
            "Coal-to-electric boiler",
            "Coal-to-air-to-water heat pump",
        ]

        for intervention in interventions:
            with self.subTest(intervention=intervention):
                result = check_compatibility(intervention, "gas")
                self.assertEqual(result["status"], "incompatible")

    def test_mismatched_heating_system_is_incompatible(self):
        result = check_compatibility("Gas boiler retrofit", "coal")
        self.assertEqual(result["status"], "incompatible")

    def test_unknown_heating_system_needs_review(self):
        result = check_compatibility("Efficient coal boiler", "unknown")
        self.assertEqual(result["status"], "needs_review")

    def test_unmodelled_heating_system_needs_review(self):
        systems = ["district", "electric", "other"]

        for system in systems:
            with self.subTest(system=system):
                result = check_compatibility(
                    "Gas boiler retrofit", system
                )
                self.assertEqual(result["status"], "needs_review")

    def test_invalid_heating_system_is_rejected(self):
        with self.assertRaises(ValueError):
            check_compatibility("Insulation", "nuclear")

    def test_non_string_heating_system_is_rejected(self):
        for system in [None, 123, ["coal"]]:
            with self.subTest(system=system):
                with self.assertRaises(ValueError):
                    check_compatibility("Insulation", system)

    def test_unknown_intervention_is_rejected(self):
        with self.assertRaises(ValueError):
            check_compatibility("Magic energy machine", "coal")

    def test_non_string_intervention_is_rejected(self):
        for intervention in [None, 123, ["Insulation"]]:
            with self.subTest(intervention=intervention):
                with self.assertRaises(ValueError):
                    check_compatibility(intervention, "coal")

    def test_evaluate_interventions_preserves_original_data(self):
        interventions = [
            {
                "intervention": "Gas boiler retrofit",
                "investment_cost_usd": 13500,
            },
            {
                "intervention": "LED lighting",
                "investment_cost_usd": 815,
            },
        ]

        results = evaluate_interventions(interventions, "gas")

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["compatibility"], "compatible")
        self.assertEqual(results[1]["compatibility"], "compatible")
        self.assertNotIn("compatibility", interventions[0])

    def test_evaluation_keeps_incompatible_options_visible(self):
        interventions = [
            {"intervention": "Gas boiler retrofit"},
            {"intervention": "Efficient coal boiler"},
        ]

        results = evaluate_interventions(interventions, "gas")

        self.assertEqual(results[0]["compatibility"], "compatible")
        self.assertEqual(results[1]["compatibility"], "incompatible")

    def test_evaluation_keeps_fuel_switch_options_visible_for_review(self):
        interventions = [
            {"intervention": "Coal-to-electric boiler"},
            {"intervention": "Coal-to-air-to-water heat pump"},
        ]

        results = evaluate_interventions(interventions, "coal")

        for result in results:
            self.assertEqual(result["compatibility"], "needs_review")

    def test_non_dictionary_intervention_is_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_interventions(["Insulation"], "coal")

    def test_missing_intervention_name_is_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_interventions([{"investment_cost_usd": 100}], "coal")


if __name__ == "__main__":
    unittest.main()
