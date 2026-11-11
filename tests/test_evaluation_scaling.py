
import unittest

from src.evaluation import evaluate_school
from src.school_profile import create_school_profile


class TestEvaluationScaling(unittest.TestCase):

    def create_profile(self, area):
        return create_school_profile(
            climate_zone=3,
            floor_area_m2=area,
            heating_system="coal",
            heating_condition="unknown",
            available_fuels=["coal", "electricity"],
            electrical_capacity_kw=None,
        )

    def find_intervention(self, results, name):
        for item in results["interventions"]:
            if item["intervention"] == name:
                return item

        self.fail(f"Intervention not found: {name}")

    def test_reference_school_savings_remain_unchanged(self):
        profile = self.create_profile(4000)
        results = evaluate_school(profile)

        insulation = self.find_intervention(results, "Insulation")

        self.assertEqual(
            insulation["estimated_energy_saving_kwh"],
            392482,
        )

    def test_half_size_school_savings_are_scaled(self):
        profile = self.create_profile(2000)
        results = evaluate_school(profile)

        insulation = self.find_intervention(results, "Insulation")

        self.assertEqual(
            insulation["estimated_energy_saving_kwh"],
            196241,
        )

    def test_original_savings_are_preserved(self):
        profile = self.create_profile(2000)
        results = evaluate_school(profile)

        insulation = self.find_intervention(results, "Insulation")

        self.assertEqual(
            insulation["reported_energy_saving_kwh"],
            392482,
        )

    def test_investment_cost_is_not_scaled(self):
        profile = self.create_profile(2000)
        results = evaluate_school(profile)

        insulation = self.find_intervention(results, "Insulation")

        self.assertEqual(
            insulation["investment_cost_usd"],
            33043,
        )

    def test_savings_basis_is_preserved(self):
        profile = self.create_profile(2000)
        results = evaluate_school(profile)

        insulation = self.find_intervention(results, "Insulation")
        lighting = self.find_intervention(results, "LED lighting")
        electric_boiler = self.find_intervention(
            results,
            "Coal-to-electric boiler",
        )

        self.assertEqual(
            insulation["reported_saving_basis"],
            "thermal",
        )

        self.assertEqual(
            lighting["reported_saving_basis"],
            "electrical",
        )

        self.assertEqual(
            electric_boiler["reported_saving_basis"],
            "fuel_switch_unresolved",
        )

    def test_electrical_conversion_still_needs_review(self):
        profile = self.create_profile(4000)
        results = evaluate_school(profile)

        electric_boiler = self.find_intervention(
            results,
            "Coal-to-electric boiler",
        )

        self.assertEqual(
            electric_boiler["compatibility"],
            "needs_review",
        )

    def test_scaling_assumption_is_disclosed(self):
        profile = self.create_profile(2000)
        results = evaluate_school(profile)

        insulation = self.find_intervention(results, "Insulation")

        self.assertIn(
            "proportionally",
            insulation["scaling_assumption"],
        )

    def test_electric_boiler_net_savings_are_unresolved(self):
        profile = self.create_profile(2000)
        results = evaluate_school(profile)

        electric_boiler = self.find_intervention(
            results,
            "Coal-to-electric boiler",
        )

        self.assertIsNone(
            electric_boiler["estimated_energy_saving_kwh"]
        )

        self.assertEqual(
            electric_boiler["estimate_status"],
            "unresolved",
        )

        self.assertEqual(
            electric_boiler["reported_energy_saving_kwh"],
            195350,
        )

        self.assertEqual(
            electric_boiler["scaling_factor"],
            0.5,
        )

    def test_heat_pump_net_savings_are_unresolved(self):
        profile = self.create_profile(2000)
        results = evaluate_school(profile)

        heat_pump = self.find_intervention(
            results,
            "Coal-to-air-to-water heat pump",
        )

        self.assertIsNone(
            heat_pump["estimated_energy_saving_kwh"]
        )

        self.assertEqual(
            heat_pump["estimate_status"],
            "unresolved",
        )

        self.assertEqual(
            heat_pump["reported_energy_saving_kwh"],
            434627,
        )

        self.assertEqual(
            heat_pump["scaling_factor"],
            0.5,
        )

    def test_both_electrical_conversions_need_review(self):
        profile = self.create_profile(2000)
        results = evaluate_school(profile)

        for name in [
            "Coal-to-electric boiler",
            "Coal-to-air-to-water heat pump",
        ]:
            with self.subTest(intervention=name):
                item = self.find_intervention(results, name)

                self.assertEqual(
                    item["compatibility"],
                    "needs_review",
                )

    def test_unresolved_fuel_switch_limitation_is_disclosed(self):
        profile = self.create_profile(2000)
        results = evaluate_school(profile)

        for name in [
            "Coal-to-electric boiler",
            "Coal-to-air-to-water heat pump",
        ]:
            with self.subTest(intervention=name):
                item = self.find_intervention(results, name)

                self.assertIn(
                    "additional electricity",
                    item["estimate_limitation"],
                )

    def test_led_remains_a_school_specific_electrical_estimate(self):
        profile = self.create_profile(2000)
        results = evaluate_school(profile)

        lighting = self.find_intervention(results, "LED lighting")

        self.assertEqual(
            lighting["estimated_energy_saving_kwh"],
            7319,
        )

        self.assertEqual(
            lighting["estimate_status"],
            "estimated",
        )

        self.assertIsNone(
            lighting["estimate_limitation"]
        )


if __name__ == "__main__":
    unittest.main()
