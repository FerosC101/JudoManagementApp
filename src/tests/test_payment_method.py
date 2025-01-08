from flask import Flask, request, redirect, url_for
from flask_testing import TestCase
from src.app import app # Import your Flask app and database instance
from src.extension import db
from src.config import Config
from src.model import Athlete, TrainingPlan, Payment, AthleteTraining  # Import your models

class PaymentMethodTest(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_database.db'  # Use an in-memory database for testing
        return app

    def setUp(self):
        db.create_all()

        # Create sample data for testing
        athlete = Athlete(athlete_id='A001', name='Test Athlete', age=25, current_weight=70, weight_category='Lightweight')
        training_plan = TrainingPlan(training_plan_id=1, plan_name='Beginner', monthly_fee=100, weekly_fee=30, private_hourly_fee=50)
        db.session.add(athlete)
        db.session.add(training_plan)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_payment_method_get(self):
        response = self.client.get('/payment_method/A001/1/monthly')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Choose a payment method:', response.data)

    def test_payment_method_post_success(self):
        data = {'payment_method': 'credit'}
        response = self.client.post('/payment_method/A001/1/monthly', data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Payment successful and registration completed!", response.data)

        # Check if payment and athlete_training records are created
        payment = Payment.query.filter_by(athlete_id='A001', training_plan_id=1).first()
        self.assertIsNotNone(payment)
        self.assertEqual(payment.amount, 100)
        self.assertEqual(payment.payment_method, 'credit')

        athlete_training = AthleteTraining.query.filter_by(athlete_id='A001', training_plan_id=1).first()
        self.assertIsNotNone(athlete_training)

    def test_payment_method_post_invalid_payment_method(self):
        response = self.client.post('/payment_method/A001/1/monthly', data={}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Payment method is required.", response.data)

    def test_payment_method_post_invalid_session_type(self):
        response = self.client.post('/payment_method/A001/1/invalid', data={'payment_method': 'credit'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Invalid session type.", response.data)

    def test_payment_method_post_invalid_athlete_or_plan(self):
        response = self.client.post('/payment_method/invalid/1/monthly', data={'payment_method': 'credit'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Invalid athlete or training plan.", response.data)

if __name__ == '__main__':
    unittest.main()