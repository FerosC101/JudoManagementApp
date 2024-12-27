import unittest
from flask import url_for
from src.app import app, db
from src.model import Users, Athlete


class FlaskAppTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Set up the Flask test client
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory database for testing
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        cls.client = app.test_client()

        # Initialize the database
        with app.app_context():
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        # Tear down the database after tests
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_home_route(self):
        """Test the home route."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'login', response.data)  # Check if login form is present

    def test_register_and_login(self):
        """Test the register and login functionality."""
        # Register a new user
        response = self.client.post('/register', data={
            'name': 'John Doe',
            'age': '25',
            'current_weight': '70',
            'weight_category': 'Middleweight',
            'role': 'user'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'login', response.data)  # Should redirect to login page

        # Verify the new user is in the database
        with app.app_context():
            athlete = Athlete.query.filter_by(first_name='John').first()
            self.assertIsNotNone(athlete)
            user = Users.query.filter_by(athlete_id=athlete.athlete_id).first()
            self.assertIsNotNone(user)

        # Login with the new user
        response = self.client.post('/login', data={'user_id': user.user_id}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'user_dashboard', response.data)  # Should redirect to user dashboard

    def test_dashboard_requires_login(self):
        """Test that the dashboard route requires login."""
        response = self.client.get('/dashboard', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'login', response.data)  # Should redirect to login page

    def test_guest_view(self):
        """Test the guest view route."""
        # Add a test athlete to the database
        with app.app_context():
            athlete = Athlete(
                athlete_id="25-0001",
                first_name="Jane",
                last_name="Doe",
                age=22,
                weight_category="Lightweight",
                contact_info="jane.doe@example.com"
            )
            db.session.add(athlete)
            db.session.commit()

        # Access the guest view
        response = self.client.get('/guest')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Jane Doe', response.data)  # Check if the athlete appears on the page


if __name__ == '__main__':
    unittest.main()
