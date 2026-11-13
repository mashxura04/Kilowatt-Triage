import http.client
import json
import threading
import unittest
from http.server import HTTPServer
from unittest import mock

import api.evaluate as api_module
from api.evaluate import handler


def valid_profile(**changes):
    profile = {
        "climate_zone": 3,
        "floor_area_m2": 4000,
        "heating_system": "coal",
        "heating_condition": "fair",
        "available_fuels": ["coal"],
        "electrical_capacity_kw": None,
    }
    profile.update(changes)
    return profile


class ApiHandlerTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Silence the handler's diagnostic messages during tests.
        cls._log_patch = mock.patch.object(
            api_module, "log", lambda message: None
        )
        cls._log_patch.start()

        class QuietHandler(handler):
            def log_message(self, format, *args):
                pass

        cls.server = HTTPServer(("127.0.0.1", 0), QuietHandler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(
            target=cls.server.serve_forever,
            daemon=True,
        )
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)
        cls._log_patch.stop()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def send(self, method, path, body=None):
        connection = http.client.HTTPConnection(
            "127.0.0.1", self.port, timeout=10
        )
        try:
            headers = {}
            if body is not None:
                headers["Content-Type"] = "application/json"
            connection.request(method, path, body=body, headers=headers)
            response = connection.getresponse()
            raw = response.read()
        finally:
            connection.close()

        try:
            data = json.loads(raw)
        except ValueError:
            self.fail(f"Response was not valid JSON: {raw[:200]!r}")

        return response.status, data

    def post_payload(self, payload):
        return self.send(
            "POST",
            "/api/evaluate",
            json.dumps(payload).encode("utf-8"),
        )

    def post_raw(self, raw_text):
        return self.send(
            "POST",
            "/api/evaluate",
            raw_text.encode("utf-8"),
        )

    def assert_clean_rejection(self, status, data):
        self.assertEqual(status, 400)
        self.assertIs(data["success"], False)
        self.assertIn("error", data)

    # ------------------------------------------------------------------
    # Health check and routing
    # ------------------------------------------------------------------
    def test_health_check_reports_alive(self):
        status, data = self.send("GET", "/api/evaluate")

        self.assertEqual(status, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["imports_ok"])

    def test_unknown_path_returns_json_404(self):
        status, data = self.send("GET", "/api/nothing-here")

        self.assertEqual(status, 404)
        self.assertIs(data["success"], False)

    # ------------------------------------------------------------------
    # Valid requests
    # ------------------------------------------------------------------
    def test_valid_request_returns_full_result(self):
        status, data = self.post_payload(
            {"profile": valid_profile(), "budget_usd_2021": 50000}
        )

        self.assertEqual(status, 200)
        self.assertTrue(data["success"])
        self.assertIn("evaluation", data)
        self.assertIn("package", data)
        self.assertIn("budget_optimization", data)

        self.assertAlmostEqual(
            data["package"]["thermal_savings_kwh"], 581406.0
        )
        self.assertAlmostEqual(
            data["package"]["total_investment_cost_usd_2021"], 47358.0
        )

    def test_incompatible_gas_boiler_has_no_estimate_via_api(self):
        status, data = self.post_payload({"profile": valid_profile()})

        self.assertEqual(status, 200)

        gas_boiler = next(
            item
            for item in data["evaluation"]["interventions"]
            if item["intervention"] == "Gas boiler retrofit"
        )

        self.assertIsNone(gas_boiler["estimated_energy_saving_kwh"])
        self.assertEqual(gas_boiler["estimate_status"], "not_applicable")

    def test_request_without_budget_omits_optimization(self):
        status, data = self.post_payload({"profile": valid_profile()})

        self.assertEqual(status, 200)
        self.assertNotIn("budget_optimization", data)

    # ------------------------------------------------------------------
    # Malformed requests
    # ------------------------------------------------------------------
    def test_malformed_json_returns_400(self):
        status, data = self.post_raw("{this is not json")
        self.assert_clean_rejection(status, data)

    def test_empty_body_returns_400(self):
        status, data = self.send("POST", "/api/evaluate", b"")
        self.assert_clean_rejection(status, data)

    def test_json_array_body_returns_400(self):
        status, data = self.post_raw("[1, 2, 3]")
        self.assert_clean_rejection(status, data)

    def test_missing_profile_returns_400(self):
        status, data = self.post_payload({"budget_usd_2021": 50000})
        self.assert_clean_rejection(status, data)

    def test_profile_that_is_not_an_object_returns_400(self):
        status, data = self.post_payload({"profile": "coal school"})
        self.assert_clean_rejection(status, data)

    # ------------------------------------------------------------------
    # Invalid values
    # ------------------------------------------------------------------
    def test_invalid_profile_values_return_400(self):
        bad_changes = [
            {"floor_area_m2": 0},
            {"floor_area_m2": -5},
            {"floor_area_m2": "big"},
            {"floor_area_m2": True},
            {"climate_zone": 0},
            {"climate_zone": 5},
            {"heating_system": "wood"},
            {"electrical_capacity_kw": -1},
        ]

        for changes in bad_changes:
            with self.subTest(changes=changes):
                status, data = self.post_payload(
                    {"profile": valid_profile(**changes)}
                )
                self.assert_clean_rejection(status, data)

    def test_missing_profile_field_returns_400(self):
        profile = valid_profile()
        del profile["heating_system"]

        status, data = self.post_payload({"profile": profile})
        self.assert_clean_rejection(status, data)

    def test_invalid_budgets_return_400(self):
        for budget in [-1, "abc", None]:
            with self.subTest(budget=budget):
                status, data = self.post_payload(
                    {"profile": valid_profile(), "budget_usd_2021": budget}
                )
                self.assert_clean_rejection(status, data)

    def test_nan_floor_area_returns_400(self):
        # Python's JSON parser accepts the non-standard literal NaN.
        raw = (
            '{"profile": {"climate_zone": 3, "floor_area_m2": NaN, '
            '"heating_system": "coal", "heating_condition": "fair", '
            '"available_fuels": [], "electrical_capacity_kw": null}}'
        )
        status, data = self.post_raw(raw)
        self.assert_clean_rejection(status, data)

    def test_infinite_floor_area_returns_400(self):
        # 1e999 overflows to infinity when parsed.
        raw = (
            '{"profile": {"climate_zone": 3, "floor_area_m2": 1e999, '
            '"heating_system": "coal", "heating_condition": "fair", '
            '"available_fuels": [], "electrical_capacity_kw": null}}'
        )
        status, data = self.post_raw(raw)
        self.assert_clean_rejection(status, data)

    def test_extremely_large_area_is_not_a_server_error(self):
        status, data = self.post_payload(
            {
                "profile": valid_profile(floor_area_m2=1e300),
                "budget_usd_2021": 50000,
            }
        )

        self.assertIn(status, (200, 400))


if __name__ == "__main__":
    unittest.main()