from sqlalchemy.sql import text  # Import `text` for raw SQL queries
from src.extension import db
from flask import Flask

def test_sqlalchemy_connection():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://vince:426999@localhost:5432/judo_management"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        try:
            # Use `text()` to wrap the raw SQL query
            result = db.session.execute(text("SELECT 1;"))
            print("SQLAlchemy connection successful! Result:", result.fetchone())
        except Exception as e:
            print("Failed to connect using SQLAlchemy:", e)

test_sqlalchemy_connection()
