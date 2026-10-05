import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import httpx
from google import genai

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("experiment", ROOT / "experiment.py")
experiment = importlib.util.module_from_spec(spec)
spec.loader.exec_module(experiment)


class ExperimentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "cases.json").write_text((ROOT / "cases.json").read_text())
        self.root_patch = patch.object(experiment, "ROOT", self.root)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)

    def test_preview_never_calls_gemini(self):
        with patch.object(experiment, "call_gemini") as request, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(experiment.main(["--case", "bound-query", "--preview"]), 0)
        request.assert_not_called()
        self.assertFalse((self.root / "runs").exists())

    def test_missing_key_never_calls_gemini(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(experiment, "call_gemini") as request:
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                experiment.main(["--case", "bound-query", "--expectation", "My prediction"])
        request.assert_not_called()

    def run_with_transport(self, status, payload):
        requests = []

        def handler(request):
            requests.append(request)
            record = json.loads(next((self.root / "runs").glob("*.json")).read_text())
            self.assertEqual(record["expectation_before_run"], "My prediction")
            self.assertEqual(record["status"], "prepared")
            return httpx.Response(status, json=payload)

        real_client = genai.Client

        def fake_transport_client(**kwargs):
            options = kwargs["http_options"]
            self.assertEqual(options.retry_options.attempts, 1)
            options.httpx_client = httpx.Client(transport=httpx.MockTransport(handler))
            return real_client(**kwargs)

        output = io.StringIO()
        with patch.dict(os.environ, {"GEMINI_API_KEY": "synthetic-test-key"}), patch.object(genai, "Client", side_effect=fake_transport_client), contextlib.redirect_stdout(output):
            result = experiment.main(["--case", "bound-query", "--expectation", "My prediction"])
        record = json.loads(next((self.root / "runs").glob("*.json")).read_text())
        self.assertEqual(len(requests), 1)
        self.assertNotIn("synthetic-test-key", output.getvalue())
        self.assertNotIn("synthetic-test-key", json.dumps(record))
        return result, record

    def test_actual_sdk_saves_mocked_response_after_one_request(self):
        result, record = self.run_with_transport(200, {
            "candidates": [{"content": {"role": "model", "parts": [{"text": "Synthetic test response."}]}, "finishReason": "STOP"}],
            "modelVersion": "synthetic-test-model"
        })
        self.assertEqual(result, 0)
        self.assertEqual(record["response_text"], "Synthetic test response.")
        self.assertEqual(record["status"], "completed")

    def test_rate_limit_is_recorded_without_retry(self):
        result, record = self.run_with_transport(429, {
            "error": {"code": 429, "message": "synthetic-test-key", "status": "RESOURCE_EXHAUSTED"}
        })
        self.assertEqual(result, 1)
        self.assertEqual(record["status"], "failed")
        self.assertEqual(record["http_status"], 429)


if __name__ == "__main__":
    unittest.main()
