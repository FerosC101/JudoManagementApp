from src.extension import db
from datetime import datetime


# Athlete Model
class Athlete(db.Model):
    __tablename__ = 'athletes'
    athlete_id = db.Column(db.String(10), primary_key=True)  # Format: '25-0001'
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    current_weight = db.Column(db.Float, nullable=False)
    weight_category = db.Column(db.String(20), nullable=True)

    @staticmethod
    def generate_athlete_id():
        last_athlete = Athlete.query.order_by(Athlete.athlete_id.desc()).first()
        if last_athlete:
            last_number = int(last_athlete.athlete_id.split("-")[1])
            new_number = last_number + 1
        else:
            new_number = 1
        current_year = datetime.now().strftime('%y')  # Get the last two digits of the current year
        return f"{current_year}-{new_number:04d}"


# Training Plan Model
class TrainingPlan(db.Model):
    __tablename__ = 'training_plans'
    training_plan_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    plan_name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    monthly_fee = db.Column(db.Float, nullable=False)


# Competition Model
class Competition(db.Model):
    __tablename__ = 'competitions'
    competition_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    competition_name = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=True)
    date = db.Column(db.Date, nullable=True)


# Payment Model
class Payment(db.Model):
    __tablename__ = 'payments'
    payment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    athlete_id = db.Column(db.String(10), db.ForeignKey('athletes.athlete_id'), nullable=False)
    training_plan_id = db.Column(db.Integer, db.ForeignKey('training_plans.training_plan_id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)


# Users Model
class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.String(20), primary_key=True)
    role = db.Column(db.String(50), nullable=False)
    athlete_id = db.Column(db.String(10), db.ForeignKey('athletes.athlete_id'), unique=True)

    athlete = db.relationship('Athlete', backref='user')

    __table_args__ = (
        db.CheckConstraint("role IN ('athlete', 'guest')", name="check_role"),
    )


# AthleteCompetition Model
class AthleteCompetition(db.Model):
    __tablename__ = 'athlete_competitions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    athlete_id = db.Column(db.String(10), db.ForeignKey('athletes.athlete_id'), nullable=False)
    competition_id = db.Column(db.Integer, db.ForeignKey('competitions.competition_id'), nullable=False)
    registration_date = db.Column(db.Date, nullable=False)

    athlete = db.relationship('Athlete', backref='competitions')
    competition = db.relationship('Competition', backref='participants')


# AthleteTraining Model
class AthleteTraining(db.Model):
    __tablename__ = 'athlete_trainings'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    athlete_id = db.Column(db.String(10), db.ForeignKey('athletes.athlete_id'), nullable=False)
    training_plan_id = db.Column(db.Integer, db.ForeignKey('training_plans.training_plan_id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)

    athlete = db.relationship('Athlete', backref='trainings')
    training_plan = db.relationship('TrainingPlan', backref='athlete_assignments')


# Raw SQL Table Creation
class RawSQL:
    @staticmethod
    def create_tables(cur):
        cur.execute('''CREATE TABLE IF NOT EXISTS athletes (
            athlete_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            current_weight REAL NOT NULL,
            weight_category TEXT
        );''')

        cur.execute('''CREATE TABLE IF NOT EXISTS training_plans (
            training_plan_id SERIAL PRIMARY KEY,
            plan_name TEXT NOT NULL,
            description TEXT,
            monthly_fee REAL NOT NULL
        );''')

        cur.execute('''CREATE TABLE IF NOT EXISTS athlete_trainings (
            id SERIAL PRIMARY KEY,
            athlete_id TEXT NOT NULL,
            training_plan_id INTEGER NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE,
            FOREIGN KEY (athlete_id) REFERENCES athletes(athlete_id) ON DELETE CASCADE,
            FOREIGN KEY (training_plan_id) REFERENCES training_plans(training_plan_id) ON DELETE CASCADE
        );''')

        cur.execute('''CREATE TABLE IF NOT EXISTS competitions (
            competition_id SERIAL PRIMARY KEY,
            competition_name TEXT NOT NULL,
            date DATE,
            location TEXT
        );''')

        cur.execute('''CREATE TABLE IF NOT EXISTS athlete_competitions (
            id SERIAL PRIMARY KEY,
            athlete_id TEXT NOT NULL,
            competition_id INTEGER NOT NULL,
            registration_date DATE NOT NULL,
            FOREIGN KEY (athlete_id) REFERENCES athletes(athlete_id) ON DELETE CASCADE,
            FOREIGN KEY (competition_id) REFERENCES competitions(competition_id) ON DELETE CASCADE
        );''')

        cur.execute('''CREATE TABLE IF NOT EXISTS payments (
            payment_id SERIAL PRIMARY KEY,
            athlete_id TEXT NOT NULL,
            training_plan_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            payment_date DATE NOT NULL DEFAULT CURRENT_DATE,
            payment_method TEXT NOT NULL,
            FOREIGN KEY (athlete_id) REFERENCES athletes(athlete_id) ON DELETE CASCADE,
            FOREIGN KEY (training_plan_id) REFERENCES training_plans(training_plan_id) ON DELETE CASCADE
        );''')

        cur.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            role TEXT NOT NULL CHECK (role IN ('athlete', 'guest')),
            athlete_id TEXT UNIQUE,
            FOREIGN KEY (athlete_id) REFERENCES athletes(athlete_id) ON DELETE CASCADE
        );''')
