import unittest

from src.main import calculate_baseline, calculate_after_insulation


class TestModel(unittest.TestCase):

    def test_baseline_calculations(self):
        expected = {
            1: 502080,
            2: 745280,
            3: 925800,
            4: 949720,
        }

        for zone, total in expected.items():
            with self.subTest(zone=zone):
                result = calculate_baseline(zone)
                self.assertEqual(result["total_kwh"], total)

    def test_insulation_calculations(self):
        expected = {
            1: 255273,
            2: 407699,
            3: 503798,
            4: 529111,
        }

        for zone, heating_after in expected.items():
            with self.subTest(zone=zone):
                result = calculate_after_insulation(zone)
                self.assertEqual(
                    result["heating_after_kwh"],
                    heating_after
                )

    def test_invalid_climate_zone(self):
        with self.assertRaises(ValueError):
            calculate_baseline(5)


if __name__ == "__main__":
    unittest.main()