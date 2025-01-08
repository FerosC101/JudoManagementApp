from src.extension import db
from datetime import datetime
from sqlalchemy import Enum

## Athlete Model
class Athlete(db.Model):
    __tablename__ = 'athletes'
    athlete_id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    current_weight = db.Column(db.Float, nullable=False)
    weight_category = db.Column(db.String(20), nullable=True)

    # Relationships with cascade on the "one" side
    athlete_trainings = db.relationship('AthleteTraining', backref='athlete_for_training', lazy=True, cascade='all, delete-orphan')
    athlete_competitions = db.relationship('AthleteCompetition', backref='athlete_for_competition', lazy=True, cascade='all, delete-orphan')
    athlete_payments = db.relationship('Payment', backref='athlete_for_payment', lazy=True, cascade='all, delete-orphan')

    @staticmethod
    def generate_athlete_id():
        last_athlete = Athlete.query.order_by(Athlete.athlete_id.desc()).first()
        last_number = int(last_athlete.athlete_id.split('-')[1]) if last_athlete else 0
        return f"{datetime.now().strftime('%y')}-{last_number + 1:04d}"


# Training Plan Model
class TrainingPlan(db.Model):
    __tablename__ = 'training_plans'
    training_plan_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    plan_name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    monthly_fee = db.Column(db.Float, nullable=False)
    weekly_fee = db.Column(db.Float, nullable=True)
    private_hourly_fee = db.Column(db.Float, nullable=True)
    category = db.Column(db.String(20), nullable=False)
    session_per_week = db.Column(db.Integer, nullable=True)

    # Relationships with cascade on the "one" side
    athlete_assignments = db.relationship('AthleteTraining', backref='training_plan', lazy=True, cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='training_plan', lazy=True, cascade='all, delete-orphan')


# Competition Model
class Competition(db.Model):
    __tablename__ = 'competitions'
    competition_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    competition_name = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=True)
    date = db.Column(db.Date, nullable=True)
    weight_category = db.Column(db.String(20), nullable=False)
    entry_fee = db.Column(db.Float, nullable=False)

    # Relationship with cascade on the "one" side
    competition_participants = db.relationship('AthleteCompetition', backref='competition', lazy=True, cascade='all, delete-orphan')


# Payment Model
class Payment(db.Model):
    __tablename__ = 'payments'
    payment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    athlete_id = db.Column(db.String(10), db.ForeignKey('athletes.athlete_id'), nullable=False)
    training_plan_id = db.Column(db.Integer, db.ForeignKey('training_plans.training_plan_id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)
    plan_type = db.Column(Enum('monthly', 'weekly', 'private', name='plan_type_enum'), nullable=False)


# Users Model
class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.String(20), primary_key=True)
    role = db.Column(db.String(50), nullable=False)
    athlete_id = db.Column(db.String(10), db.ForeignKey('athletes.athlete_id'), unique=True)

    # One-to-one relationship with cascade
    athlete = db.relationship('Athlete', backref=db.backref('user', uselist=False, cascade='all, delete-orphan'), single_parent=True)

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


# AthleteTraining Model
class AthleteTraining(db.Model):
    __tablename__ = 'athlete_training'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    athlete_id = db.Column(db.String(10), db.ForeignKey('athletes.athlete_id'), nullable=False)
    training_plan_id = db.Column(db.Integer, db.ForeignKey('training_plans.training_plan_id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)