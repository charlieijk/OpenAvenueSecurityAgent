"""Exercise the loopback demo's real HTTP and SQLite boundaries."""

import http.client
import json
import threading
import unittest
from unittest.mock import patch
from http.server import ThreadingHTTPServer

from demo import DemoHandler


class DemoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), DemoHandler)
        cls.worker = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.worker.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.worker.join()

    def request(self, method, path, headers=None, body=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port)
        connection.request(method, path, body=body, headers=headers or {})
        response = connection.getresponse()
        result = response.status, response.read(), dict(response.getheaders())
        connection.close()
        return result

    def test_prompts_and_check_make_no_model_requests(self):
        with patch("experiment.call_gemini", side_effect=AssertionError("No API allowed")) as api:
            status, body, headers = self.request("GET", "/api/cases")
            self.assertEqual(status, 200)
            self.assertEqual(headers["Cache-Control"], "no-store")
            cases = json.loads(body)["cases"]
            self.assertEqual([case["id"] for case in cases], ["bound-query", "web-config", "login-log"])
            self.assertIn(cases[0]["input"], cases[0]["prompt"])
            status, body, _ = self.request("POST", "/api/verify-sqlite")
            self.assertEqual(status, 200)
            proof = json.loads(body)
            self.assertEqual(proof["returned_row"], [2, "O'Reilly"])
            self.assertEqual(proof["remaining_rows"], 2)
            api.assert_not_called()

    def test_rejects_foreign_hosts_origins_and_user_input(self):
        for headers in ({"Host": "untrusted.example"}, {"Origin": "https://untrusted.example"}):
            self.assertEqual(self.request("POST", "/api/verify-sqlite", headers)[0], 403)
        self.assertEqual(self.request("POST", "/api/verify-sqlite", body="user input")[0], 400)

    def test_only_named_assets_are_served(self):
        for path in ("/.env", "/experiment.py", "/../cases.json", "/runs"):
            self.assertEqual(self.request("GET", path)[0], 404)
        status, body, headers = self.request("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn(b"Offline coursework demo", body)
        self.assertIn("frame-ancestors 'none'", headers["Content-Security-Policy"])


if __name__ == "__main__":
    unittest.main()
