from src.extension import db

class Athlete(db.Model):
    __tablename__ = 'Athletes'
    athlete_id = db.Column(db.String(10), primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    weight_category = db.Column(db.String(20))
    contact_info = db.Column(db.String(100))
    registration_date = db.Column(db.DateTime)

    @staticmethod
    def generate_athlete_id(conn):
        try:
            cur = conn.cursor()
            cur.execute("SELECT athlete_id FROM athletes ORDER BY athlete_id DESC LIMIT 1;")
            last_id = cur.fetchone()
            if last_id:
                last_number = int(last_id[0].split("-")[1])
                new_number = last_number + 1
            else:
                new_number = 1
            current_year = "25"  # Modify the year as needed
            new_id = f"{current_year}-{new_number:04d}"
            return new_id
        except Exception as e:
            print(f"Error generating athlete_id: {e}")
            return None


class TrainingPlan(db.Model):
    __tablename__ = 'Training_Plans'
    plan_id = db.Column(db.Integer, primary_key=True)
    plan_name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)

class Competition(db.Model):
    __tablename__ = 'Competitions'
    competition_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100))
    date = db.Column(db.Date)
    weight_category = db.Column(db.String(20))

class Payment(db.Model):
    __tablename__ = 'Payments'
    payment_id = db.Column(db.Integer, primary_key=True)
    athlete_id = db.Column(db.Integer, db.ForeignKey('Athletes.athlete_id'))
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.DateTime)
    payment_method = db.Column(db.String(20), nullable=False)
    
class Users(db.Model):
    __tablename__ = 'Users'
    user_id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(50), nullable=False)
    athlete_id = db.Column(db.Integer, db.ForeignKey('Athletes.athlete_id'))

# Raw SQL Table Creation
# Not sure which one to use so I made both of them

class RawSQL:
    def create_tables(self, cur):
        cur.execute('''CREATE TABLE IF NOT EXISTS athletes (
            athlete_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            age INT NOT NULL,
            current_weight REAL NOT NULL,
            weight_category TEXT NOT NULL
        );''')

        cur.execute('''CREATE TABLE IF NOT EXISTS training_plans (
            training_plan_id SERIAL PRIMARY KEY,
            plan_name TEXT NOT NULL,
            description TEXT NOT NULL,
            monthly_fee REAL NOT NULL
        );''')

        cur.execute('''CREATE TABLE IF NOT EXISTS athlete_training (
            id SERIAL PRIMARY KEY,
            athlete_id TEXT NOT NULL,
            training_plan_id INT NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE,
            FOREIGN KEY (athlete_id) REFERENCES athletes(athlete_id),
            FOREIGN KEY (training_plan_id) REFERENCES training_plans(training_plan_id)
        );''')

        cur.execute('''CREATE TABLE IF NOT EXISTS competition (
            competition_id SERIAL PRIMARY KEY,
            competition_name TEXT NOT NULL,
            date DATE NOT NULL,
            location TEXT NOT NULL
        );''')

        cur.execute('''CREATE TABLE IF NOT EXISTS athlete_competition (
            id SERIAL PRIMARY KEY,
            athlete_id TEXT NOT NULL,
            competition_id INT NOT NULL,
            registration_date DATE NOT NULL,
            FOREIGN KEY (athlete_id) REFERENCES athletes(athlete_id),
            FOREIGN KEY (competition_id) REFERENCES competition(competition_id)
        );''')

        cur.execute('''CREATE TABLE IF NOT EXISTS payments (
            payment_id SERIAL PRIMARY KEY,
            athlete_id TEXT NOT NULL,
            training_plan_id INT NOT NULL,
            amount REAL NOT NULL,
            payment_date DATE NOT NULL,
            FOREIGN KEY (athlete_id) REFERENCES athletes(athlete_id),
            FOREIGN KEY (training_plan_id) REFERENCES training_plans(training_plan_id)
        );''')

        cur.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            role TEXT NOT NULL CHECK (role IN ('athlete', 'guest')),
            athlete_id TEXT UNIQUE,
            FOREIGN KEY (athlete_id) REFERENCES athletes(athlete_id) ON DELETE CASCADE
        );''')
