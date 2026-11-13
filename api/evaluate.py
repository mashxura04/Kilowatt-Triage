
import json
import sys
from pathlib import Path

from http.server import BaseHTTPRequestHandler

# Make the repository root importable.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.evaluation import evaluate_school
from src.package_evaluation import evaluate_retrofit_package
from src.budget_optimizer import optimize_retrofit_budget


class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        if self.path != "/api/evaluate":
            self.send_error(404, "Endpoint not found")
            return

        try:
            content_length = int(
                self.headers.get("Content-Length", 0)
            )

            if content_length <= 0 or content_length > 100_000:
                self.send_error(400, "Invalid request size")
                return

            payload = json.loads(
                self.rfile.read(content_length)
            )

            if not isinstance(payload, dict):
                raise ValueError(
                    "Request body must be a JSON object."
                )

            profile = payload.get("profile")

            if not isinstance(profile, dict):
                raise ValueError(
                    "A school profile is required."
                )

            # Run the existing school evaluation.
            evaluation = evaluate_school(profile)

            # Evaluate the compatible retrofit package.
            package = evaluate_retrofit_package(profile)

            response = {
                "success": True,
                "evaluation": evaluation,
                "package": package,
            }

            # Run budget optimization when a budget is provided.
            if "budget_usd_2021" in payload:
                budget = payload["budget_usd_2021"]

                optimization = optimize_retrofit_budget(
                    profile,
                    budget,
                )

                response["budget_optimization"] = optimization

            self._send_json(200, response)

        except (
            ValueError,
            TypeError,
            KeyError,
            json.JSONDecodeError,
        ) as error:
            self._send_json(
                400,
                {
                    "success": False,
                    "error": str(error),
                },
            )

        except Exception:
            self._send_json(
                500,
                {
                    "success": False,
                    "error": "An internal evaluation error occurred.",
                },
            )

    def _send_json(self, status_code, data):
        body = json.dumps(
            data,
            allow_nan=False,
        ).encode("utf-8")

        self.send_response(status_code)
        self.send_header(
            "Content-Type",
            "application/json",
        )
        self.send_header(
            "Content-Length",
            str(len(body)),
        )
        self.send_header(
            "Cache-Control",
            "no-store",
        )
        self.end_headers()
        self.wfile.write(body)
