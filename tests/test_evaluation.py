
import unittest

from src.evaluation import (
    evaluate_school,
    evaluate_school_interventions,
)
from src.school_profile import create_school_profile


class TestSchoolEvaluation(unittest.TestCase):

    def make_profile(
        self,
        heating_system="coal",
        available_fuels=None,
        electrical_capacity_kw=None,
    ):
        if available_fuels is None:
            available_fuels = []

        return create_school_profile(
            climate_zone=3,
            floor_area_m2=4000,
            heating_system=heating_system,
            available_fuels=available_fuels,
            electrical_capacity_kw=electrical_capacity_kw,
        )

    def find_intervention(self, results, name):
        for item in results:
            if item["intervention"] == name:
                return item

        self.fail(f"Intervention not found: {name}")

    def test_evaluation_returns_six_zone_interventions(self):
        profile = self.make_profile()
        results = evaluate_school_interventions(profile)

        self.assertEqual(len(results), 6)

    def test_evaluation_uses_school_climate_zone(self):
        profile = self.make_profile()
        results = evaluate_school_interventions(profile)

        for item in results:
            self.assertEqual(item["climate_zone"], 3)

    def test_coal_school_gets_compatible_coal_boiler_option(self):
        profile = self.make_profile()
        results = evaluate_school_interventions(profile)

        coal_boiler = self.find_intervention(
            results,
            "Efficient coal boiler",
        )

        self.assertEqual(coal_boiler["compatibility"], "compatible")

    def test_coal_school_does_not_get_gas_boiler_as_compatible(self):
        profile = self.make_profile()
        results = evaluate_school_interventions(profile)

        gas_boiler = self.find_intervention(
            results,
            "Gas boiler retrofit",
        )

        self.assertEqual(gas_boiler["compatibility"], "incompatible")

    def test_electric_conversion_needs_review_when_fuel_unknown(self):
        profile = self.make_profile()
        results = evaluate_school_interventions(profile)

        electric_boiler = self.find_intervention(
            results,
            "Coal-to-electric boiler",
        )

        self.assertEqual(
            electric_boiler["compatibility"],
            "needs_review",
        )

    def test_electric_conversion_needs_review_when_capacity_unknown(self):
        profile = self.make_profile(
            available_fuels=["coal", "electricity"],
        )

        results = evaluate_school_interventions(profile)

        electric_boiler = self.find_intervention(
            results,
            "Coal-to-electric boiler",
        )

        self.assertEqual(electric_boiler["compatibility"], "needs_review")
        self.assertIn(
            "capacity is unknown",
            electric_boiler["compatibility_reason"],
        )

    def test_electric_conversion_needs_review_even_when_capacity_is_known(self):
        profile = self.make_profile(
            available_fuels=["coal", "electricity"],
            electrical_capacity_kw=100,
        )

        results = evaluate_school_interventions(profile)

        electric_boiler = self.find_intervention(
            results,
            "Coal-to-electric boiler",
        )

        self.assertEqual(electric_boiler["compatibility"], "needs_review")
        self.assertIn(
            "required electrical load",
            electric_boiler["compatibility_reason"],
        )

    def test_heat_pump_needs_review_even_when_capacity_is_known(self):
        profile = self.make_profile(
            available_fuels=["coal", "electricity"],
            electrical_capacity_kw=100,
        )

        results = evaluate_school_interventions(profile)

        heat_pump = self.find_intervention(
            results,
            "Coal-to-air-to-water heat pump",
        )

        self.assertEqual(heat_pump["compatibility"], "needs_review")
        self.assertIn(
            "required electrical load",
            heat_pump["compatibility_reason"],
        )

    def test_no_electricity_produces_specific_explanation(self):
        profile = self.make_profile(
            available_fuels=["coal"],
        )

        results = evaluate_school_interventions(profile)

        for name in [
            "Coal-to-electric boiler",
            "Coal-to-air-to-water heat pump",
        ]:
            with self.subTest(intervention=name):
                item = self.find_intervention(results, name)

                self.assertEqual(item["compatibility"], "needs_review")
                self.assertIn(
                    "electricity is available",
                    item["compatibility_reason"],
                )

    def test_insulation_and_led_remain_compatible(self):
        profile = self.make_profile()
        results = evaluate_school_interventions(profile)

        for name in ["Insulation", "LED lighting"]:
            with self.subTest(intervention=name):
                item = self.find_intervention(results, name)
                self.assertEqual(item["compatibility"], "compatible")

    def test_missing_profile_fields_are_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_school_interventions({
                "climate_zone": 3,
                "heating_system": "coal",
            })

    def test_non_dictionary_profile_is_rejected(self):
        for invalid_profile in [None, [], "school"]:
            with self.subTest(profile=invalid_profile):
                with self.assertRaises(ValueError):
                    evaluate_school(invalid_profile)

    def test_invalid_profile_values_are_rejected(self):
        valid_profile = self.make_profile()

        invalid_cases = [
            ("climate_zone", 99),
            ("floor_area_m2", -100),
            ("heating_system", "something"),
            ("available_fuels", "coal"),
            ("electrical_capacity_kw", -10),
        ]

        for field, invalid_value in invalid_cases:
            with self.subTest(field=field):
                profile = valid_profile.copy()
                profile[field] = invalid_value

                with self.assertRaises(ValueError):
                    evaluate_school(profile)

    def test_returned_profile_has_an_independent_fuel_list(self):
        profile = self.make_profile(
            available_fuels=["coal", "electricity"],
        )

        results = evaluate_school(profile)

        results["school_profile"]["available_fuels"].append("natural_gas")

        self.assertEqual(
            profile["available_fuels"],
            ["coal", "electricity"],
        )


if __name__ == "__main__":
    unittest.main()
