"""Kilowatt Triage API handler.

POST /api/evaluate  -> runs the school evaluation, retrofit package
                       evaluation and (optionally) budget optimization.
GET  /api/evaluate  -> health check; confirms the handler runs and shows
                       import status. Extra detail only in development.

Diagnostics: progress messages go to stderr (visible in the Vercel dev
terminal and in Vercel function logs). Python tracebacks are included in
HTTP responses ONLY in development (VERCEL_ENV=development) or when the
environment variable KT_DEBUG=1 is set.
"""

import faulthandler
import json
import os
import sys
import traceback
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

try:
    # If Python crashes hard (not a normal exception), print a traceback.
    faulthandler.enable()
except Exception:
    pass

DEBUG = (
    os.environ.get("KT_DEBUG") == "1"
    or os.environ.get("VERCEL_ENV", "development") == "development"
)

ACCEPTED_PATHS = ("/api/evaluate", "/api/evaluate.py")


def log(message):
    print(f"[kilowatt] {message}", file=sys.stderr, flush=True)


# Make the repository root importable.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import the calculation modules, but never let an import problem kill
# the process silently. The error is stored and reported instead.
IMPORT_ERROR = None
try:
    from src.evaluation import evaluate_school
    from src.package_evaluation import evaluate_retrofit_package
    from src.budget_optimizer import optimize_retrofit_budget
except BaseException:
    IMPORT_ERROR = traceback.format_exc()
    log("IMPORT FAILED:\n" + IMPORT_ERROR)

if IMPORT_ERROR is None:
    log(
        f"module loaded OK (python {sys.version.split()[0]}, "
        f"cwd={os.getcwd()}, project_root={PROJECT_ROOT}, debug={DEBUG})"
    )


class handler(BaseHTTPRequestHandler):

    # ------------------------------------------------------------------
    # GET: health check
    # ------------------------------------------------------------------
    def do_GET(self):
        log(f"GET received: path={self.path}")

        if self._clean_path() not in ACCEPTED_PATHS:
            self._send_json(
                404,
                {"success": False, "error": "Endpoint not found."},
            )
            return

        info = {
            "success": True,
            "status": "alive",
            "imports_ok": IMPORT_ERROR is None,
        }

        if DEBUG:
            data_dir = PROJECT_ROOT / "data"
            src_dir = PROJECT_ROOT / "src"
            info["debug"] = {
                "python": sys.version,
                "executable": sys.executable,
                "cwd": os.getcwd(),
                "project_root": str(PROJECT_ROOT),
                "data_dir_exists": data_dir.is_dir(),
                "data_files": (
                    sorted(p.name for p in data_dir.iterdir())
                    if data_dir.is_dir()
                    else []
                ),
                "src_files": (
                    sorted(p.name for p in src_dir.iterdir())
                    if src_dir.is_dir()
                    else []
                ),
                "import_error": IMPORT_ERROR,
            }

        self._send_json(200, info)

    # ------------------------------------------------------------------
    # POST: run the assessment
    # ------------------------------------------------------------------
    def do_POST(self):
        stage = "start"
        try:
            log(f"POST received: path={self.path}")

            if self._clean_path() not in ACCEPTED_PATHS:
                self._send_json(
                    404,
                    {"success": False, "error": "Endpoint not found."},
                )
                return

            if IMPORT_ERROR is not None:
                self._send_json(
                    500,
                    self._error_body(
                        "The calculation modules failed to load.",
                        stage="import",
                        trace=IMPORT_ERROR,
                    ),
                )
                return

            stage = "read request"
            log(f"stage: {stage}")
            content_length = int(self.headers.get("Content-Length", 0))

            if content_length <= 0 or content_length > 100_000:
                self._send_json(
                    400,
                    {"success": False, "error": "Invalid request size."},
                )
                return

            stage = "parse JSON"
            log(f"stage: {stage}")
            payload = json.loads(self.rfile.read(content_length))

            if not isinstance(payload, dict):
                raise ValueError("Request body must be a JSON object.")

            profile = payload.get("profile")

            if not isinstance(profile, dict):
                raise ValueError("A school profile is required.")

            if DEBUG:
                log(f"payload keys: {sorted(payload)}")
                log(f"profile received: {json.dumps(profile, default=str)}")
                if "budget_usd_2021" in payload:
                    log(f"budget received: {payload['budget_usd_2021']!r}")

            stage = "evaluate_school"
            log(f"stage: {stage}")
            evaluation = evaluate_school(profile)

            stage = "evaluate_retrofit_package"
            log(f"stage: {stage}")
            package = evaluate_retrofit_package(profile)

            response = {
                "success": True,
                "evaluation": evaluation,
                "package": package,
            }

            if "budget_usd_2021" in payload:
                stage = "optimize_retrofit_budget"
                log(f"stage: {stage}")
                response["budget_optimization"] = optimize_retrofit_budget(
                    profile,
                    payload["budget_usd_2021"],
                )

            stage = "send response"
            log(f"stage: {stage}")
            self._send_json(200, response)
            log("POST finished OK")

        except (ValueError, TypeError, KeyError) as error:
            trace = traceback.format_exc()
            log(f"REQUEST ERROR at stage '{stage}':\n{trace}")
            self._send_json(
                400,
                self._error_body(str(error), stage=stage, trace=trace),
            )

        except Exception:
            trace = traceback.format_exc()
            log(f"INTERNAL ERROR at stage '{stage}':\n{trace}")
            self._send_json(
                500,
                self._error_body(
                    "An internal evaluation error occurred.",
                    stage=stage,
                    trace=trace,
                ),
            )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _clean_path(self):
        """Request path without the query string or a trailing slash."""
        return urlparse(self.path).path.rstrip("/") or "/"

    @staticmethod
    def _error_body(message, stage=None, trace=None):
        body = {"success": False, "error": message}
        if stage:
            body["stage"] = stage
        if DEBUG and trace:
            body["traceback"] = trace
        return body

    def _send_json(self, status_code, data):
        try:
            body = json.dumps(data, allow_nan=False).encode("utf-8")
        except (TypeError, ValueError) as error:
            # The results contained NaN, infinity or a non-JSON type.
            log("RESPONSE SERIALIZATION FAILED:\n" + traceback.format_exc())
            status_code = 500
            fallback = {
                "success": False,
                "error": "The results could not be converted to JSON.",
                "stage": "serialize",
            }
            if DEBUG:
                fallback["detail"] = str(error)
            body = json.dumps(fallback).encode("utf-8")

        try:
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            log("Client disconnected before the response was sent.")