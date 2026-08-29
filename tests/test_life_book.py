"""Unit tests for the Flagship Comprehensive Vedic Life Book PDF report."""

import os
import unittest

from app import billing, db as database


class TestLifeBook(unittest.TestCase):
    def setUp(self):
        import time
        os.environ["ASTRO_GATEWAY"] = "test"
        os.makedirs("var", exist_ok=True)
        database.Base.metadata.create_all(database.engine)
        self.db = database.session()
        self.user = database.User(
            email=f"lifebook_{time.time()}@example.com",
            name="Life Book Native",
            phone="9876543210",
            provider="test",
            provider_sub=f"test_lb_{time.time()}"
        )
        self.db.add(self.user)
        self.db.commit()
        self.db.refresh(self.user)

    def tearDown(self):
        self.db.close()

    def test_life_book_product_in_catalogue(self):
        prod = billing.PRODUCTS.get("life_book")
        self.assertIsNotNone(prod)
        self.assertEqual(prod.sku, "life_book")
        self.assertEqual(prod.pages, 35)
        self.assertEqual(prod.amount_paise, 49900)

    def test_life_book_order_and_gating(self):
        # 1. Unpaid check
        paid_order = billing.has_paid_report(self.db, self.user, sku="life_book")
        self.assertIsNone(paid_order)

        # 2. Create order
        order, _ = billing.create_order(
            self.db, self.user, sku="life_book", report_topic="life_book"
        )
        self.assertEqual(order.sku, "life_book")
        self.assertEqual(order.status, database.OrderStatus.created)

        # 3. Mark paid
        import time
        granted, msg = billing.mark_paid(self.db, order, f"lb_txn_{time.time()}")
        self.assertTrue(granted)
        self.assertEqual(order.status, database.OrderStatus.paid)

        # 4. Gating now succeeds
        paid_order = billing.has_paid_report(self.db, self.user, sku="life_book")
        self.assertIsNotNone(paid_order)
        self.assertEqual(paid_order.id, order.id)


if __name__ == "__main__":
    unittest.main()
