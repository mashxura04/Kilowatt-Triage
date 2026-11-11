import unittest
from unittest.mock import patch

from src.main import calculate_baseline, calculate_after_insulation


class TestBaselineModel(unittest.TestCase):

    def test_all_climate_zone_baselines(self):
        expected_totals = {
            1: 502080,
            2: 745280,
            3: 925800,
            4: 949720,
        }

        for zone, expected in expected_totals.items():
            with self.subTest(zone=zone):
                results = calculate_baseline(zone)
                self.assertEqual(results["total_kwh"], expected)

    def test_all_baseline_components(self):
        expected = {
            1: (472560, 22520, 7000),
            2: (715760, 22520, 7000),
            3: (896280, 22520, 7000),
            4: (920200, 22520, 7000),
        }

        for zone, values in expected.items():
            with self.subTest(zone=zone):
                results = calculate_baseline(zone)

                self.assertEqual(results["heating_kwh"], values[0])
                self.assertEqual(results["lighting_kwh"], values[1])
                self.assertEqual(results["equipment_kwh"], values[2])

                self.assertEqual(
                    results["total_kwh"],
                    sum(values),
                )

    def test_all_climate_zone_insulation(self):
        expected = {
            1: (217287, 255273),
            2: (308061, 407699),
            3: (392482, 503798),
            4: (391089, 529111),
        }

        for zone, values in expected.items():
            with self.subTest(zone=zone):
                results = calculate_after_insulation(zone)

                self.assertEqual(results["heating_saved_kwh"], values[0])
                self.assertEqual(results["heating_after_kwh"], values[1])

                self.assertGreaterEqual(
                    results["heating_after_kwh"],
                    0,
                )

    def test_insulation_saving_percentages(self):
        expected = {
            1: 46.0,
            2: 43.04,
            3: 43.79,
            4: 42.50,
        }

        for zone, percentage in expected.items():
            with self.subTest(zone=zone):
                results = calculate_after_insulation(zone)

                self.assertAlmostEqual(
                    results["saving_percentage"],
                    percentage,
                    delta=0.05,
                )

    def test_custom_school_area_baseline(self):
        results = calculate_baseline(3, 2000)

        self.assertEqual(results["heating_kwh"], 448140)
        self.assertEqual(results["lighting_kwh"], 11260)
        self.assertEqual(results["equipment_kwh"], 3500)
        self.assertEqual(results["total_kwh"], 462900)

    def test_custom_school_area_insulation(self):
        results = calculate_after_insulation(3, 2000)

        self.assertEqual(results["heating_before_kwh"], 448140)
        self.assertEqual(results["heating_saved_kwh"], 196241)
        self.assertEqual(results["heating_after_kwh"], 251899)

    def test_invalid_climate_zones(self):
        for zone in [0, 5, -1, True]:
            with self.subTest(zone=zone):
                with self.assertRaises(ValueError):
                    calculate_baseline(zone)

    def test_invalid_insulation_zone(self):
        with self.assertRaises(ValueError):
            calculate_after_insulation(5)

    def test_invalid_school_areas(self):
        invalid_areas = [
            0,
            -1,
            float("nan"),
            float("inf"),
            float("-inf"),
            True,
        ]

        for area in invalid_areas:
            with self.subTest(area=area):
                with self.assertRaises(ValueError):
                    calculate_baseline(1, area)

                with self.assertRaises(ValueError):
                    calculate_after_insulation(1, area)

    def test_missing_insulation_record(self):
        with patch(
            "src.baseline.get_interventions_by_zone",
            return_value=[],
        ):
            with self.assertRaisesRegex(
                ValueError,
                "exactly one insulation record",
            ):
                calculate_after_insulation(1)

    def test_duplicate_insulation_records(self):
        record = {
            "intervention": "Insulation",
            "reported_energy_saving_kwh": 100,
            "reported_saving_basis": "thermal",
        }

        with patch(
            "src.baseline.get_interventions_by_zone",
            return_value=[record, record],
        ):
            with self.assertRaisesRegex(
                ValueError,
                "exactly one insulation record",
            ):
                calculate_after_insulation(1)

    def test_nonthermal_insulation_saving_is_rejected(self):
        record = {
            "intervention": "Insulation",
            "reported_energy_saving_kwh": 100,
            "reported_saving_basis": "electrical",
        }

        with patch(
            "src.baseline.get_interventions_by_zone",
            return_value=[record],
        ):
            with self.assertRaisesRegex(
                ValueError,
                "classified as thermal",
            ):
                calculate_after_insulation(1)

    def test_negative_insulation_saving_is_rejected(self):
        record = {
            "intervention": "Insulation",
            "reported_energy_saving_kwh": -100,
            "reported_saving_basis": "thermal",
        }

        with patch(
            "src.baseline.get_interventions_by_zone",
            return_value=[record],
        ):
            with self.assertRaisesRegex(
                ValueError,
                "non-negative number",
            ):
                calculate_after_insulation(1)

    def test_nonfinite_insulation_saving_is_rejected(self):
        for saving in [float("nan"), float("inf")]:
            record = {
                "intervention": "Insulation",
                "reported_energy_saving_kwh": saving,
                "reported_saving_basis": "thermal",
            }

            with self.subTest(saving=saving):
                with patch(
                    "src.baseline.get_interventions_by_zone",
                    return_value=[record],
                ):
                    with self.assertRaisesRegex(
                        ValueError,
                        "non-negative number",
                    ):
                        calculate_after_insulation(1)


if __name__ == "__main__":
    unittest.main()