"""Unit tests for the upgraded Admin Panel endpoints."""

import os
import time
import unittest
from fastapi.testclient import TestClient

from app import db as database
try:
    from app.main import app
except ImportError:
    app = None


class TestAdminAPI(unittest.TestCase):
    def setUp(self):
        if app is None:
            self.skipTest("itsdangerous / web dependencies not installed locally")
        os.environ["ASTRO_GATEWAY"] = "test"
        os.environ["ASTRO_ADMIN_EMAILS"] = "admin_test@divineastro.org"
        os.makedirs("var", exist_ok=True)
        database.Base.metadata.create_all(database.engine)
        self.db = database.session()
        self.client = TestClient(app)

        # Create admin user
        t = time.time()
        self.admin_user = database.User(
            email="admin_test@divineastro.org",
            name="Admin User",
            provider="test",
            provider_sub=f"adm_sub_{t}",
            is_admin=True,
        )
        # Create normal user
        self.normal_user = database.User(
            email=f"customer_{t}@example.com",
            name="Customer User",
            provider="test",
            provider_sub=f"cust_sub_{t}",
            is_admin=False,
        )
        self.db.add(self.admin_user)
        self.db.add(self.normal_user)
        self.db.commit()
        self.db.refresh(self.admin_user)
        self.db.refresh(self.normal_user)

    def test_metrics_endpoint(self):
        # Override auth dependency
        from app.api_account import me
        app.dependency_overrides[me] = lambda: self.admin_user
        try:
            res = self.client.get("/api/admin/metrics")
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertIn("revenue_all_rupees", data)
            self.assertIn("total_users", data)
            self.assertIn("products", data)
            self.assertIn("recent_orders", data)
        finally:
            app.dependency_overrides.pop(me, None)

    def test_users_and_credit_adjustment(self):
        from app.api_account import me
        app.dependency_overrides[me] = lambda: self.admin_user
        try:
            # 1. List users
            res = self.client.get("/api/admin/users")
            self.assertEqual(res.status_code, 200)
            users = res.json()["users"]
            self.assertTrue(len(users) >= 2)

            # 2. Adjust credits for normal user
            adj_res = self.client.post(
                f"/api/admin/users/{self.normal_user.id}/credits",
                json={"delta": 10, "note": "Welcome VIP bonus"},
            )
            self.assertEqual(adj_res.status_code, 200)
            self.assertEqual(adj_res.json()["new_balance"], 10)

            # 3. Block user
            blk_res = self.client.post(
                f"/api/admin/users/{self.normal_user.id}/block",
                json={"blocked": True},
            )
            self.assertEqual(blk_res.status_code, 200)
            self.assertTrue(blk_res.json()["blocked"])
        finally:
            app.dependency_overrides.pop(me, None)

    def test_system_health_endpoint(self):
        from app.api_account import me
        app.dependency_overrides[me] = lambda: self.admin_user
        try:
            res = self.client.get("/api/admin/system-health")
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertIn("database", data)
            self.assertIn("ephemeris", data)
            self.assertIn("llm", data)
            self.assertIn("gateways", data)
        finally:
            app.dependency_overrides.pop(me, None)


if __name__ == "__main__":
    unittest.main()
