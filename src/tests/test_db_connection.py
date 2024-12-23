import unittest
from src.Database import create_connection
import psycopg2

class TestDatabaseConnection(unittest.TestCase):
    def test_successful_connection(self):
        try:
            conn = create_connection()
            self.assertIsNotNone(conn, "Connection should not be None.")
            self.assertTrue(conn.closed == 0, "Connection should be open.")
        finally:
            if conn and conn.closed == 0:
                conn.close()

    def test_failed_connection(self):
        def mock_connect_to_db():
            return psycopg2.connect(
                dbname="wrong_db",
                user="wrong_user",
                password="wrong_pass",
                host="localhost",
                port="5432"
            )
        with self.assertRaises(psycopg2.OperationalError):
            mock_connect_to_db()

if __name__ == '__main__':
    unittest.main()
