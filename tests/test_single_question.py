"""Test suite for single-question paid reports and payment gating."""

import datetime as dt
import unittest

from app import billing, db as database
from app.chart_service import BirthData, build
from app.pdf_report import single_question_pdf


import os

class TestSingleQuestion(unittest.TestCase):
    def setUp(self):
        os.environ["ASTRO_GATEWAY"] = "test"
        database.Base.metadata.create_all(database.engine)
        self.db = database.session()
        self.user = database.User(
            email=f"tester_{dt.datetime.now().timestamp()}@example.com",
            name="Test Native",
            phone="9999999999",
            provider="test",
            provider_sub=f"test_sub_{dt.datetime.now().timestamp()}"
        )
        self.db.add(self.user)
        self.db.commit()
        self.db.refresh(self.user)

    def tearDown(self):
        self.db.close()

    def test_single_question_catalogue(self):
        sq_products = billing.catalogue(kind="single_question")
        self.assertEqual(len(sq_products), 3)
        skus = [p["sku"] for p in sq_products]
        self.assertIn("sq_career", skus)
        self.assertIn("sq_marriage_timing", skus)
        self.assertIn("sq_wealth_business", skus)

    def test_order_creation_and_gating(self):
        # 1. Initially user has no paid report
        has_paid = billing.has_paid_report(self.db, self.user, sku="sq_career")
        self.assertIsNone(has_paid)

        # 2. Create order
        order, checkout = billing.create_order(
            self.db, self.user, sku="sq_career", report_topic="sq_career"
        )
        self.assertEqual(order.sku, "sq_career")
        self.assertEqual(order.report_topic, "sq_career")
        self.assertEqual(order.status, database.OrderStatus.created)

        # Still unpaid
        has_paid = billing.has_paid_report(self.db, self.user, sku="sq_career")
        self.assertIsNone(has_paid)

        # 3. Mark order as paid
        granted, msg = billing.mark_paid(self.db, order, f"test_pay_id_{dt.datetime.now().timestamp()}")
        self.assertEqual(order.status, database.OrderStatus.paid)

        # Now has_paid returns the order
        has_paid = billing.has_paid_report(self.db, self.user, sku="sq_career")
        self.assertIsNotNone(has_paid)
        self.assertEqual(has_paid.id, order.id)

    def test_pdf_generation(self):
        from app import chart_service
        if chart_service.ChartBuilder is None:
            self.skipTest("stellium ephemeris engine not available in local environment")
        birth = BirthData(
            name="Test Native", date="1990-01-01", time="12:00",
            latitude=28.6139, longitude=77.2090, timezone="Asia/Kolkata",
            place="New Delhi, India", zodiac="sidereal",
            ayanamsa="lahiri", house_system="Whole Sign"
        )
        session = build(birth)

        # English single-question report
        pdf_bytes_en = single_question_pdf(session, topic="sq_career", language="en")
        self.assertTrue(len(pdf_bytes_en) > 1000)
        self.assertTrue(pdf_bytes_en.startswith(b"%PDF"))

        # Hindi single-question report
        pdf_bytes_hi = single_question_pdf(session, topic="sq_marriage_timing", language="hi")
        self.assertTrue(len(pdf_bytes_hi) > 1000)
        self.assertTrue(pdf_bytes_hi.startswith(b"%PDF"))


if __name__ == "__main__":
    unittest.main()
