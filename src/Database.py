import psycopg2
from psycopg2 import sql

def create_connection():
    # edit db details :3
    try:
        conn = psycopg2.connect(
            dbname = "judo_management",
            user = "vince",
            password = "426999",
            host = "localhost",
            port = "5432",
        )

        return conn

    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None


def create_table():
    global cur, conn
    try:
        conn = create_connection()
        cur = conn.cursor()

        cur.execute('''
            CREATE TABLE IF NOT EXISTS athletes (
                athlete_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                age INT NOT NULL,
                current_weight REAL NOT NULL,
                weight_category TEXT NOT NULL
            );
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS training_plans(
                training_plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_name TEXT NOT NULL,
                description TEXT NOT NULL,
                monthly_fee REAL NOT NULL
            );
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS athlete_training(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                athlete_id TEXT NOT NULL,
                training_plan_id INTEGER NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE,
                FOREIGN KEY athlete_id REFERENCES athletes(athlete_id),
                FOREIGN KEY training_plan_id REFERENCES training_plans(training_plan_id)
            );
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS competition(
                competition_id INTEGER PRIMARY KEY AUTOINCREMENT,
                competition_name TEXT NOT NULL,
                date DATE NOT NULL,
                location TEXT NOT NULL,
            );
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS athlete_competition(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                athlete_id TEXT NOT NULL,
                competition_id INTEGER NOT NULL,
                registration_date DATE NOT NULL,
                FOREIGN KEY athlete_id REFERENCES athletes(athlete_id),
                FOREIGN KEY competition_id REFERENCES competition(competition_id)
            );
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                athlete_id TEXT NOT NULL,
                training_plan_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                payment_date DATE NOT NULL,
                FOREIGN KEY (athlete_id) REFERENCES athletes(athlete_id),
                FOREIGN KEY (training_plan_id) REFERENCES training_plans(training_plan_id)
            );
        ''')

        conn.commit()
        print("Table created successfully")

    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

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

        current_year = "25"
        new_id = f"{current_year}-{new_number:04d}"
        return new_id
    except Exception as e:
        print(f"Error generating custom_id: {e}")
        return None
