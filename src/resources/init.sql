-- Drop existing tables in reverse dependency order with CASCADE
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS athlete_competition CASCADE;
DROP TABLE IF EXISTS competition CASCADE;
DROP TABLE IF EXISTS athlete_training CASCADE;
DROP TABLE IF EXISTS training_plans CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS athletes CASCADE;

-- Create tables
CREATE TABLE athletes (
    athlete_id TEXT PRIMARY KEY,  -- Changed to TEXT to match the format (e.g., '24-0001')
    name TEXT NOT NULL,
    age INTEGER NOT NULL,
    current_weight REAL NOT NULL,
    weight_category TEXT
);

CREATE TABLE training_plans (
    training_plan_id SERIAL PRIMARY KEY,
    plan_name TEXT NOT NULL,
    description TEXT,
    monthly_fee REAL NOT NULL
);

CREATE TABLE athlete_training (
    id SERIAL PRIMARY KEY,
    athlete_id TEXT NOT NULL,  -- Changed to TEXT to match athlete_id in athletes table
    training_plan_id INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    FOREIGN KEY (athlete_id) REFERENCES athletes(athlete_id) ON DELETE CASCADE,
    FOREIGN KEY (training_plan_id) REFERENCES training_plans(training_plan_id) ON DELETE CASCADE
);

CREATE TABLE competitions IF NOT EXISTS (
    competition_id SERIAL PRIMARY KEY,
    competition_name TEXT NOT NULL,
    date DATE,
    location TEXT
);

CREATE TABLE athlete_competitions (
    id SERIAL PRIMARY KEY,
    athlete_id TEXT NOT NULL,  -- Changed to TEXT to match athlete_id in athletes table
    competition_id INTEGER NOT NULL,
    registration_date DATE NOT NULL,
    FOREIGN KEY (athlete_id) REFERENCES athletes(athlete_id) ON DELETE CASCADE,
    FOREIGN KEY (competition_id) REFERENCES competitions(competition_id) ON DELETE CASCADE
);

CREATE TABLE payments (
    payment_id SERIAL PRIMARY KEY,
    athlete_id TEXT NOT NULL,  -- Changed to TEXT to match athlete_id in athletes table
    training_plan_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    payment_date DATE NOT NULL DEFAULT CURRENT_DATE,
    payment_method TEXT NOT NULL,
    FOREIGN KEY (athlete_id) REFERENCES athletes(athlete_id) ON DELETE CASCADE,
    FOREIGN KEY (training_plan_id) REFERENCES training_plans(training_plan_id) ON DELETE CASCADE
);

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    role TEXT NOT NULL CHECK (role IN ('athlete', 'guest')),
    athlete_id TEXT UNIQUE,  -- Changed to TEXT to match athlete_id in athletes table
    FOREIGN KEY (athlete_id) REFERENCES athletes(athlete_id) ON DELETE CASCADE
);
ALTER TABLE users
ALTER COLUMN user_id TYPE TEXT;
