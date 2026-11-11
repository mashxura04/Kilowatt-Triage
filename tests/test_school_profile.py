
import unittest

from src.school_profile import create_school_profile


class TestSchoolProfile(unittest.TestCase):

    def test_valid_school_profile(self):
        profile = create_school_profile(
            climate_zone=3,
            floor_area_m2=4000,
            heating_system="coal",
            heating_condition="fair",
            available_fuels=["coal", "electricity"],
            electrical_capacity_kw=100,
        )

        self.assertEqual(profile["climate_zone"], 3)
        self.assertEqual(profile["floor_area_m2"], 4000)
        self.assertEqual(profile["heating_system"], "coal")

    def test_unknown_information_is_preserved(self):
        profile = create_school_profile(
            climate_zone=3,
            floor_area_m2=4000,
            heating_system="unknown",
        )

        self.assertEqual(profile["heating_condition"], "unknown")
        self.assertEqual(profile["available_fuels"], [])
        self.assertIsNone(profile["electrical_capacity_kw"])

    def test_invalid_climate_zone(self):
        with self.assertRaises(ValueError):
            create_school_profile(5, 4000, "coal")

    def test_boolean_climate_zone_is_rejected(self):
        with self.assertRaises(ValueError):
            create_school_profile(True, 4000, "coal")

    def test_non_integer_climate_zone_is_rejected(self):
        with self.assertRaises(ValueError):
            create_school_profile(3.0, 4000, "coal")

    def test_invalid_floor_area(self):
        with self.assertRaises(ValueError):
            create_school_profile(3, 0, "coal")

    def test_negative_floor_area_is_rejected(self):
        with self.assertRaises(ValueError):
            create_school_profile(3, -100, "coal")

    def test_nonfinite_floor_areas_are_rejected(self):
        for area in [float("nan"), float("inf"), float("-inf")]:
            with self.subTest(area=area):
                with self.assertRaises(ValueError):
                    create_school_profile(3, area, "coal")

    def test_boolean_floor_area_is_rejected(self):
        with self.assertRaises(ValueError):
            create_school_profile(3, True, "coal")

    def test_non_numeric_floor_area_is_rejected(self):
        with self.assertRaises(ValueError):
            create_school_profile(3, "4000", "coal")

    def test_invalid_heating_system(self):
        with self.assertRaises(ValueError):
            create_school_profile(3, 4000, "nuclear")

    def test_non_string_heating_system_is_rejected(self):
        with self.assertRaises(ValueError):
            create_school_profile(3, 4000, None)

    def test_invalid_heating_condition(self):
        with self.assertRaises(ValueError):
            create_school_profile(
                3, 4000, "coal", heating_condition="excellent"
            )

    def test_non_string_heating_condition_is_rejected(self):
        with self.assertRaises(ValueError):
            create_school_profile(
                3, 4000, "coal", heating_condition=None
            )

    def test_invalid_fuel(self):
        with self.assertRaises(ValueError):
            create_school_profile(
                3, 4000, "coal", available_fuels=["petrol"]
            )

    def test_non_list_fuels_are_rejected(self):
        with self.assertRaises(ValueError):
            create_school_profile(
                3, 4000, "coal", available_fuels=("coal",)
            )

    def test_non_string_fuel_is_rejected(self):
        with self.assertRaises(ValueError):
            create_school_profile(
                3, 4000, "coal", available_fuels=["coal", None]
            )

    def test_unhashable_fuel_is_rejected(self):
        with self.assertRaises(ValueError):
            create_school_profile(
                3, 4000, "coal", available_fuels=[["coal"]]
            )

    def test_invalid_electrical_capacity(self):
        with self.assertRaises(ValueError):
            create_school_profile(
                3, 4000, "coal", electrical_capacity_kw=0
            )

    def test_negative_electrical_capacity_is_rejected(self):
        with self.assertRaises(ValueError):
            create_school_profile(
                3, 4000, "coal", electrical_capacity_kw=-100
            )

    def test_nonfinite_electrical_capacities_are_rejected(self):
        for capacity in [float("nan"), float("inf"), float("-inf")]:
            with self.subTest(capacity=capacity):
                with self.assertRaises(ValueError):
                    create_school_profile(
                        3, 4000, "coal",
                        electrical_capacity_kw=capacity,
                    )

    def test_boolean_electrical_capacity_is_rejected(self):
        with self.assertRaises(ValueError):
            create_school_profile(
                3, 4000, "coal", electrical_capacity_kw=True
            )

    def test_non_numeric_electrical_capacity_is_rejected(self):
        with self.assertRaises(ValueError):
            create_school_profile(
                3, 4000, "coal", electrical_capacity_kw="100"
            )

    def test_available_fuels_are_not_modified(self):
        fuels = ["coal", "electricity"]

        profile = create_school_profile(
            3, 4000, "coal", available_fuels=fuels
        )

        profile["available_fuels"].append("natural_gas")

        self.assertEqual(fuels, ["coal", "electricity"])


if __name__ == "__main__":
    unittest.main()
