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

ALTER TABLE training_plans
ADD COLUMN session_per_week INT;

-- Insert Training Plans
INSERT INTO training_plans (plan_name, description, monthly_fee, weekly_fee, private_hourly_fee, category, session_per_week)
VALUES
    ('Beginner Judo',
     'Introduction to judo fundamentals, including basic techniques and movements.',
     1000.00,
     1000.00 / 4,
     500.00,
     'Beginner',
     3),

    ('Intermediate Judo',
     'For judokas who have mastered the basics and are ready for intermediate throws and groundwork techniques.',
     2000.00,
     2000.00 / 4,
     700.00,
     'Intermediate',
     4),

    ('Advanced Competition Prep',
     'Focused on competition techniques, conditioning, and strategy for elite athletes.',
     5000.00,
     5000.00 / 4,
     1200.00,
     'Elite',
     5);

-- Insert Competitions
INSERT INTO competitions (competition_name, location, date, weight_category, entry_fee)
VALUES
    ('City Judo Championship',
     'Batangas City Sports Center',
     '2025-02-15',
     'Under 60kg',
     500.00),

    ('Southern Luzon Regional Judo Meet',
     'Calamba Coliseum',
     '2025-03-10',
     'Under 75kg',
     800.00),

    ('Philippine National Judo Cup',
     'Manila Arena',
     '2025-05-20',
     'Open Weight',
     1500.00);
