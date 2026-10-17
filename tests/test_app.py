import os
import tempfile
import unittest
from fastapi.testclient import TestClient

# Use an isolated database for deterministic tests.
fd, path = tempfile.mkstemp(suffix=".db")
os.close(fd)
os.environ["PULSEGUARD_DB"] = path

from app import app, init_db
init_db()
client = TestClient(app)

class PulseGuardTests(unittest.TestCase):
    def test_dashboard_and_static_assets_load(self):
        page = client.get("/")
        self.assertEqual(page.status_code, 200)
        self.assertIn("PulseGuard Z", page.text)
        css = client.get("/static/styles.css")
        self.assertEqual(css.status_code, 200)
        self.assertIn("--ink", css.text)
        js = client.get("/static/app.js")
        self.assertEqual(js.status_code, 200)

    def test_health_endpoint(self):
        response = client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_inventory_is_seeded(self):
        response = client.get("/api/inventory")
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.json()["count"], 10)

    def test_summary_totals_match_inventory(self):
        items = client.get("/api/inventory").json()["items"]
        summary = client.get("/api/summary").json()
        self.assertEqual(summary["total_items"], len(items))
        self.assertEqual(summary["critical_items"] + summary["high_risk_items"] +
                         summary["risk_breakdown"]["MEDIUM"] + summary["risk_breakdown"]["LOW"], len(items))

    def test_search_filter(self):
        result = client.get("/api/inventory?q=saline").json()
        self.assertGreaterEqual(result["count"], 1)
        self.assertTrue(all("saline" in x["name"].lower() for x in result["items"]))

    def test_simulation_does_not_modify_inventory(self):
        before = client.get("/api/inventory").json()["items"]
        response = client.post("/api/simulate", json={"sku":"MED-001","demand_multiplier":2,"stock_delta":0})
        after = client.get("/api/inventory").json()["items"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["note"], "Scenario only; no inventory records were changed.")
        self.assertEqual(before, after)

    def test_unknown_sku_returns_404(self):
        response = client.post("/api/simulate", json={"sku":"NOT-REAL","demand_multiplier":1.5})
        self.assertEqual(response.status_code, 404)

    def test_invalid_multiplier_rejected(self):
        response = client.post("/api/simulate", json={"sku":"MED-001","demand_multiplier":99})
        self.assertEqual(response.status_code, 422)

if __name__ == "__main__":
    unittest.main()
