import psycopg2
from psycopg2 import sql
from src.config import DB_CONFIG


def create_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None

def create_table():
    try:
        conn = create_connection()
        cur = conn.cursor()

        # Create tables
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
            CREATE TABLE IF NOT EXISTS training_plans (
                training_plan_id SERIAL PRIMARY KEY,
                plan_name TEXT NOT NULL,
                description TEXT NOT NULL,
                monthly_fee REAL NOT NULL
            );
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS athlete_training (
                id SERIAL PRIMARY KEY,
                athlete_id TEXT NOT NULL,
                training_plan_id INT NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE,
                FOREIGN KEY (athlete_id) REFERENCES athletes(athlete_id),
                FOREIGN KEY (training_plan_id) REFERENCES training_plans(training_plan_id)
            );
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS competition (
                competition_id SERIAL PRIMARY KEY,
                competition_name TEXT NOT NULL,
                date DATE NOT NULL,
                location TEXT NOT NULL
            );
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS athlete_competition (
                id SERIAL PRIMARY KEY,
                athlete_id TEXT NOT NULL,
                competition_id INT NOT NULL,
                registration_date DATE NOT NULL,
                FOREIGN KEY (athlete_id) REFERENCES athletes(athlete_id),
                FOREIGN KEY (competition_id) REFERENCES competition(competition_id)
            );
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                payment_id SERIAL PRIMARY KEY,
                athlete_id TEXT NOT NULL,
                training_plan_id INT NOT NULL,
                amount REAL NOT NULL,
                payment_date DATE NOT NULL,
                FOREIGN KEY (athlete_id) REFERENCES athletes(athlete_id),
                FOREIGN KEY (training_plan_id) REFERENCES training_plans(training_plan_id)
            );
        ''')

        conn.commit()
        print("Tables created successfully.")
    except psycopg2.Error as e:
        print(f"Error creating tables: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
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

        current_year = "25"  # Adjust this logic if needed for dynamic year handling
        new_id = f"{current_year}-{new_number:04d}"
        return new_id
    except Exception as e:
        print(f"Error generating athlete_id: {e}")
        return None

def add_athlete(name, age, current_weight, weight_category):
    if not all([name, age, current_weight, weight_category]):
        print("All fields are required to add an athlete.")
        return

    try:
        conn = create_connection()
        if not conn:
            return

        athlete_id = generate_athlete_id(conn)
        if not athlete_id:
            raise ValueError("Error generating athlete_id")

        cur = conn.cursor()
        cur.execute('''
            INSERT INTO athletes(athlete_id, name, age, current_weight, weight_category) 
            VALUES (%s, %s, %s, %s, %s);
        ''', (athlete_id, name, age, current_weight, weight_category))

        conn.commit()
        print(f"Athlete {athlete_id} added successfully.")
    except Exception as e:
        print(f"Error adding athlete: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

def get_all_athletes():
    try:
        conn = create_connection()
        if not conn:
            return []

        cur = conn.cursor()
        cur.execute("SELECT * FROM athletes ORDER BY athlete_id;")
        athletes = cur.fetchall()
        return athletes
    except Exception as e:
        print(f"Error retrieving athletes: {e}")
        return []
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

def update_athlete(athlete_id, name=None, age=None, weight_category=None):
    if not athlete_id:
        print("Athlete ID is required to update an athlete.")
        return

    try:
        conn = create_connection()
        if not conn:
            return

        cur = conn.cursor()
        updates = []
        values = []

        if name:
            updates.append("name = %s")
            values.append(name)
        if age:
            updates.append("age = %s")
            values.append(age)
        if weight_category:
            updates.append("weight_category = %s")
            values.append(weight_category)

        if not updates:
            print("No fields provided to update.")
            return

        values.append(athlete_id)
        query = sql.SQL("UPDATE athletes SET {updates} WHERE athlete_id = %s").format(
            updates=sql.SQL(", ").join(sql.SQL(u) for u in updates)
        )
        cur.execute(query, values)
        conn.commit()
        print(f"Athlete with ID {athlete_id} updated successfully.")
    except Exception as e:
        print(f"Error updating athlete: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

def delete_athlete(athlete_id):
    if not athlete_id:
        print("Athlete ID is required to delete an athlete.")
        return

    try:
        conn = create_connection()
        if not conn:
            return

        cur = conn.cursor()
        cur.execute('DELETE FROM athletes WHERE athlete_id = %s', (athlete_id,))
        conn.commit()
        print(f"Athlete with ID {athlete_id} deleted successfully.")
    except Exception as e:
        print(f"Error deleting athlete: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()
