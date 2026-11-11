
import unittest

from src.package_evaluation import evaluate_retrofit_package
from src.school_profile import create_school_profile


class TestPackageEvaluation(unittest.TestCase):

    def create_profile(
        self,
        climate_zone=3,
        floor_area_m2=4000,
        heating_system="coal",
    ):
        return create_school_profile(
            climate_zone=climate_zone,
            floor_area_m2=floor_area_m2,
            heating_system=heating_system,
            heating_condition="unknown",
            available_fuels=["coal", "electricity"],
            electrical_capacity_kw=None,
        )

    def test_coal_package_includes_insulation_and_boiler(self):
        result = evaluate_retrofit_package(self.create_profile())
        names = [item["intervention"] for item in result["selected_measures"]]

        self.assertIn("Insulation", names)
        self.assertIn("Efficient coal boiler", names)
        self.assertIn("LED lighting", names)

    def test_zone_three_sequential_heating_calculation(self):
        result = evaluate_retrofit_package(self.create_profile())

        self.assertAlmostEqual(result["baseline_heating_kwh"], 896280)
        self.assertAlmostEqual(result["heating_after_insulation_kwh"], 503798)
        self.assertAlmostEqual(result["heating_after_package_kwh"], 314874)

    def test_thermal_savings_are_not_double_counted(self):
        result = evaluate_retrofit_package(self.create_profile())

        self.assertAlmostEqual(result["thermal_savings_kwh"], 392482 + 188924)
        self.assertAlmostEqual(
            result["thermal_savings_kwh"],
            result["baseline_heating_kwh"] - result["heating_after_package_kwh"],
        )

    def test_led_savings_are_reported_separately(self):
        result = evaluate_retrofit_package(self.create_profile())

        self.assertAlmostEqual(result["electrical_savings_kwh"], 14638)

        led = next(
            item for item in result["selected_measures"]
            if item["intervention"] == "LED lighting"
        )
        self.assertEqual(led["energy_carrier"], "electrical")

    def test_half_size_school_savings_are_scaled(self):
        result = evaluate_retrofit_package(
            self.create_profile(floor_area_m2=2000)
        )

        self.assertAlmostEqual(result["thermal_savings_kwh"], (392482 + 188924) / 2)
        self.assertAlmostEqual(result["electrical_savings_kwh"], 14638 / 2)
        self.assertAlmostEqual(result["heating_after_package_kwh"], 314874 / 2)

    def test_gas_school_includes_gas_boiler_package(self):
        result = evaluate_retrofit_package(
            self.create_profile(heating_system="gas")
        )
        names = [item["intervention"] for item in result["selected_measures"]]

        self.assertIn("Insulation", names)
        self.assertIn("Gas boiler retrofit", names)
        self.assertIn("LED lighting", names)
        self.assertNotIn("Efficient coal boiler", names)

    def test_gas_school_uses_sequential_heating_calculation(self):
        result = evaluate_retrofit_package(
            self.create_profile(heating_system="gas")
        )

        self.assertAlmostEqual(result["baseline_heating_kwh"], 896280)
        self.assertAlmostEqual(result["heating_after_insulation_kwh"], 503798)
        self.assertAlmostEqual(result["heating_after_package_kwh"], 341113)

    def test_gas_school_thermal_savings_are_correct(self):
        result = evaluate_retrofit_package(
            self.create_profile(heating_system="gas")
        )

        self.assertAlmostEqual(result["thermal_savings_kwh"], 392482 + 162685)
        self.assertAlmostEqual(
            result["thermal_savings_kwh"],
            result["baseline_heating_kwh"] - result["heating_after_package_kwh"],
        )

    def test_gas_school_led_savings_remain_separate(self):
        result = evaluate_retrofit_package(
            self.create_profile(heating_system="gas")
        )

        self.assertAlmostEqual(result["electrical_savings_kwh"], 14638)
        self.assertAlmostEqual(result["thermal_savings_kwh"], 555167)

    def test_gas_school_boiler_assumption_is_disclosed(self):
        result = evaluate_retrofit_package(
            self.create_profile(heating_system="gas")
        )

        self.assertIsNotNone(result["boiler_assumption"])
        self.assertIn("not explicitly confirmed", result["boiler_assumption"])

    def test_gas_school_investment_cost_is_correct(self):
        result = evaluate_retrofit_package(
            self.create_profile(heating_system="gas")
        )

        self.assertAlmostEqual(
            result["total_investment_cost_usd_2021"],
            33043 + 13500 + 815,
        )

    def test_fuel_switch_options_are_excluded_from_package(self):
        result = evaluate_retrofit_package(self.create_profile())

        excluded = [item["intervention"] for item in result["excluded_options"]]
        selected = [item["intervention"] for item in result["selected_measures"]]

        self.assertIn("Coal-to-electric boiler", excluded)
        self.assertIn("Coal-to-air-to-water heat pump", excluded)
        self.assertNotIn("Coal-to-electric boiler", selected)
        self.assertNotIn("Coal-to-air-to-water heat pump", selected)

    def test_investment_cost_is_sum_of_selected_measures(self):
        result = evaluate_retrofit_package(self.create_profile())

        self.assertAlmostEqual(
            result["total_investment_cost_usd_2021"],
            33043 + 13500 + 815,
        )

    def test_package_does_not_modify_original_profile(self):
        profile = self.create_profile()
        original = profile.copy()

        evaluate_retrofit_package(profile)

        self.assertEqual(profile, original)

    def test_package_discloses_methodological_limitations(self):
        result = evaluate_retrofit_package(self.create_profile())

        self.assertTrue(result["limitations"])
        self.assertIsNotNone(result["boiler_assumption"])
        self.assertTrue(
            any("not explicitly confirmed" in item for item in result["limitations"])
            or "not explicitly confirmed" in result["boiler_assumption"]
        )

    # All climate zones

    def test_coal_package_across_all_climate_zones(self):
        expected = {
            1: (472560, 159546),
            2: (715760, 254812),
            3: (896280, 314874),
            4: (920200, 330694),
        }

        for zone, values in expected.items():
            with self.subTest(zone=zone):
                result = evaluate_retrofit_package(
                    self.create_profile(climate_zone=zone)
                )
                self.assertAlmostEqual(result["baseline_heating_kwh"], values[0])
                self.assertAlmostEqual(result["heating_after_package_kwh"], values[1])

    def test_gas_package_across_all_climate_zones(self):
        expected = {
            1: (472560, 172841),
            2: (715760, 276046),
            3: (896280, 341113),
            4: (920200, 358252),
        }

        for zone, values in expected.items():
            with self.subTest(zone=zone):
                result = evaluate_retrofit_package(
                    self.create_profile(climate_zone=zone, heating_system="gas")
                )
                self.assertAlmostEqual(result["baseline_heating_kwh"], values[0])
                self.assertAlmostEqual(result["heating_after_package_kwh"], values[1])

    # Investment costs

    def test_coal_investment_costs_across_all_zones(self):
        expected = {1: 36951, 2: 47358, 3: 47358, 4: 55864}

        for zone, cost in expected.items():
            with self.subTest(zone=zone):
                result = evaluate_retrofit_package(
                    self.create_profile(climate_zone=zone)
                )
                self.assertAlmostEqual(
                    result["total_investment_cost_usd_2021"], cost
                )

    def test_gas_investment_costs_across_all_zones(self):
        expected = {1: 36951, 2: 47358, 3: 47358, 4: 55864}

        for zone, cost in expected.items():
            with self.subTest(zone=zone):
                result = evaluate_retrofit_package(
                    self.create_profile(climate_zone=zone, heating_system="gas")
                )
                self.assertAlmostEqual(
                    result["total_investment_cost_usd_2021"], cost
                )

    # Other heating systems

    def test_unsupported_heating_systems_do_not_select_boiler(self):
        for system in ["district", "electric", "other", "unknown"]:
            with self.subTest(heating_system=system):
                result = evaluate_retrofit_package(
                    self.create_profile(heating_system=system)
                )
                names = [
                    item["intervention"] for item in result["selected_measures"]
                ]

                self.assertIn("Insulation", names)
                self.assertIn("LED lighting", names)
                self.assertNotIn("Efficient coal boiler", names)
                self.assertNotIn("Gas boiler retrofit", names)
                self.assertIsNone(result["boiler_assumption"])

    def test_unsupported_heating_systems_keep_fuel_switch_excluded(self):
        for system in ["district", "electric", "other", "unknown"]:
            with self.subTest(heating_system=system):
                result = evaluate_retrofit_package(
                    self.create_profile(heating_system=system)
                )
                excluded = [
                    item["intervention"] for item in result["excluded_options"]
                ]

                self.assertIn("Coal-to-electric boiler", excluded)
                self.assertIn("Coal-to-air-to-water heat pump", excluded)

    # Energy accounting

    def test_thermal_energy_balance_across_all_zones_and_systems(self):
        for zone in [1, 2, 3, 4]:
            for system in ["coal", "gas", "district", "electric", "other", "unknown"]:
                with self.subTest(zone=zone, heating_system=system):
                    result = evaluate_retrofit_package(
                        self.create_profile(
                            climate_zone=zone,
                            heating_system=system,
                        )
                    )

                    self.assertAlmostEqual(
                        result["baseline_heating_kwh"]
                        - result["heating_after_package_kwh"],
                        result["thermal_savings_kwh"],
                    )

    def test_electrical_savings_are_not_included_in_thermal_savings(self):
        result = evaluate_retrofit_package(self.create_profile())

        self.assertNotAlmostEqual(
            result["thermal_savings_kwh"],
            result["thermal_savings_kwh"] + result["electrical_savings_kwh"],
        )

    def test_led_investment_is_included_in_package_cost(self):
        result = evaluate_retrofit_package(self.create_profile())
        led = next(
            item for item in result["selected_measures"]
            if item["intervention"] == "LED lighting"
        )

        self.assertEqual(led["investment_cost_usd_2021"], 815)


if __name__ == "__main__":
    unittest.main()
