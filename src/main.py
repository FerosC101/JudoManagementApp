from app import app
from extension import db
from src.model import Athlete, Users  # Ensure models are imported

with app.app_context():
    db.create_all()  # Create tables

if __name__ == "__main__":
    app.run(debug=True)
