from src.extension import db
from datetime import datetime

## Athlete Model
class Athlete(db.Model):
    __tablename__ = 'athletes'
    athlete_id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    current_weight = db.Column(db.Float, nullable=False)
    weight_category = db.Column(db.String(20), nullable=True)

    # Updated backrefs for relationships with unique names to avoid conflicts
    athlete_trainings = db.relationship('AthleteTraining', backref='athlete_for_training', lazy=True)
    athlete_competitions = db.relationship('AthleteCompetition', backref='athlete_for_competition', lazy=True)
    athlete_payments = db.relationship('Payment', backref='athlete_for_payment', lazy=True)

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

    # Updated backref for reverse relationship to avoid conflict
    athlete_assignments = db.relationship('AthleteTraining', backref='training_plan_for_athlete', lazy=True)


# Competition Model
class Competition(db.Model):
    __tablename__ = 'competitions'
    competition_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    competition_name = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=True)
    date = db.Column(db.Date, nullable=True)

    # Updated backref for reverse relationship to avoid conflict
    competition_participants = db.relationship('AthleteCompetition', backref='competition_for_athlete', lazy=True)


# Payment Model
class Payment(db.Model):
    __tablename__ = 'payments'
    payment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    athlete_id = db.Column(db.String(10), db.ForeignKey('athletes.athlete_id'), nullable=False)
    training_plan_id = db.Column(db.Integer, db.ForeignKey('training_plans.training_plan_id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)

    # Backref for reverse relationship
    training_plan = db.relationship('TrainingPlan', backref='payments', lazy=True)


# Users Model
class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.String(20), primary_key=True)  # Make sure this is TEXT
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

    athlete = db.relationship('Athlete', backref='athlete_for_competition')  # Updated backref name
    competition = db.relationship('Competition', backref='athletes')  # Backref for Competition


# AthleteTraining Model
class AthleteTraining(db.Model):
    __tablename__ = 'athlete_training'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    athlete_id = db.Column(db.String(10), db.ForeignKey('athletes.athlete_id'), nullable=False)
    training_plan_id = db.Column(db.Integer, db.ForeignKey('training_plans.training_plan_id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)

    athlete = db.relationship('Athlete', backref='athlete_for_training')  # Updated backref name
    training_plan = db.relationship('TrainingPlan', backref='athlete_trainings')  # Changed the backref name here

