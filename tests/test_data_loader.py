
import unittest
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory

from src.data_loader import (
    load_data,
    load_source_register,
    validate_data,
    validate_source_register,
    get_interventions_by_zone,
)


class TestDataLoader(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.rows = load_data()

    def test_dataset_contains_24_records(self):
        self.assertEqual(len(self.rows), 24)

    def test_dataset_contains_four_climate_zones(self):
        zones = {row["climate_zone"] for row in self.rows}
        self.assertEqual(zones, {1, 2, 3, 4})

    def test_all_interventions_have_valid_saving_basis(self):
        valid_bases = {
            "thermal",
            "electrical",
            "fuel_switch_unresolved",
        }

        for row in self.rows:
            self.assertIn(row["reported_saving_basis"], valid_bases)

    def test_blank_values_remain_none(self):
        for row in self.rows:
            self.assertIsNone(row["fuel_saved_tonnes"])
            self.assertIsNone(row["fuel_saved_m3"])
            self.assertIsNone(row["additional_electricity_kwh"])

    def test_investment_costs_are_positive(self):
        for row in self.rows:
            self.assertGreater(row["investment_cost_usd"], 0)

    def test_duplicate_records_are_rejected(self):
        rows = deepcopy(self.rows)
        rows.append(deepcopy(rows[0]))

        with self.assertRaises(ValueError):
            validate_data(rows)

    def test_invalid_saving_basis_is_rejected(self):
        rows = deepcopy(self.rows)
        rows[0]["reported_saving_basis"] = "unknown"

        with self.assertRaises(ValueError):
            validate_data(rows)

    def test_zone_returns_six_interventions(self):
        for zone in range(1, 5):
            with self.subTest(zone=zone):
                options = get_interventions_by_zone(zone)
                self.assertEqual(len(options), 6)

    def test_zone_returns_only_its_own_records(self):
        options = get_interventions_by_zone(3)

        for option in options:
            self.assertEqual(option["climate_zone"], 3)

    def test_invalid_zone_is_rejected(self):
        with self.assertRaises(ValueError):
            get_interventions_by_zone(5)


class TestSourceRegister(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.data_rows = load_data()
        cls.register = load_source_register(data_rows=cls.data_rows)

    def test_source_register_contains_six_entries(self):
        self.assertEqual(len(self.register), 6)

    def test_every_intervention_has_one_source_entry(self):
        dataset_names = {
            row["intervention"] for row in self.data_rows
        }

        register_names = {
            row["intervention"] for row in self.register
        }

        self.assertEqual(dataset_names, register_names)

    def test_source_register_has_no_duplicate_entries(self):
        names = [
            row["intervention"] for row in self.register
        ]

        self.assertEqual(len(names), len(set(names)))

    def test_source_register_energy_bases_match_dataset(self):
        for entry in self.register:
            matching_rows = [
                row for row in self.data_rows
                if row["intervention"] == entry["intervention"]
            ]

            expected_bases = {
                row["reported_saving_basis"]
                for row in matching_rows
            }

            self.assertEqual(
                expected_bases,
                {entry["energy_basis"]},
            )

    def test_source_register_years_match_dataset(self):
        for entry in self.register:
            matching_rows = [
                row for row in self.data_rows
                if row["intervention"] == entry["intervention"]
            ]

            expected_years = {
                row["source_year"]
                for row in matching_rows
            }

            self.assertEqual(
                expected_years,
                {entry["source_year"]},
            )

    def test_duplicate_source_entries_are_rejected(self):
        rows = deepcopy(self.register)
        rows.append(deepcopy(rows[0]))

        with self.assertRaises(ValueError):
            validate_source_register(rows, self.data_rows)

    def test_missing_source_entry_is_rejected(self):
        rows = deepcopy(self.register)
        rows.pop()

        with self.assertRaises(ValueError):
            validate_source_register(rows, self.data_rows)

    def test_incorrect_energy_basis_is_rejected(self):
        rows = deepcopy(self.register)
        rows[0]["energy_basis"] = "electrical"

        with self.assertRaises(ValueError):
            validate_source_register(rows, self.data_rows)

    def test_blank_source_documentation_is_rejected(self):
        rows = deepcopy(self.register)
        rows[0]["source_document"] = ""

        with self.assertRaises(ValueError):
            validate_source_register(rows, self.data_rows)


if __name__ == "__main__":
    unittest.main()
