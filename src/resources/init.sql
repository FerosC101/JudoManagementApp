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

INSERT INTO athletes (athlete_id, name, age, current_weight, weight_category)
VALUES
    ('24-0005', 'Anjo Santos', 22, 70.5, 'Lightweight'),
    ('24-0006', 'Kiarra Gomez', 20, 60.0, 'Featherweight'),
    ('24-0007', 'Lenard Cruz', 25, 90.2, 'Middleweight');

INSERT INTO users (user_id, role, athlete_id)
VALUES
    ('u-1001', 'athlete', '24-0005'),
    ('u-1002', 'athlete', '24-0006'),
    ('u-1003', 'athlete', '24-0007');
INSERT INTO training_plans (plan_name, description, monthly_fee)
VALUES
    ('Basic Judo Training', 'A beginner-friendly plan for mastering fundamental judo techniques.', 150.0),
    ('Advanced Grappling', 'Focused on advanced grappling and throwing techniques for competition.', 200.0),
    ('Competition Prep', 'Intensive plan for preparing for upcoming judo competitions.', 180.0);
INSERT INTO athlete_training (athlete_id, training_plan_id, start_date, end_date)
VALUES
    ('24-0005', 1, '2025-01-01', '2025-03-01'),
    ('24-0006', 2, '2025-01-10', '2025-02-10'), -- Ongoing plan
    ('24-0007', 3, '2025-01-15', '2025-02-28');
INSERT INTO competitions (competition_name, date, location)
VALUES
    ('Winter Judo Championship', '2025-02-10', 'London'),
    ('Spring Judo Open', '2025-03-15', 'Manchester'),
    ('National Judo Finals', '2025-04-20', 'Birmingham');
INSERT INTO athlete_competitions (athlete_id, competition_id, registration_date)
VALUES
    ('24-0005', 1, '2024-12-30'),
    ('24-0006', 3, '2024-12-31'),
    ('24-0007', 2, '2024-12-28');
INSERT INTO payments (athlete_id, training_plan_id, amount, payment_date, payment_method)
VALUES
    ('24-0005', 1, 150.0, '2025-01-05', 'Credit Card'),
    ('24-0006', 2, 200.0, '2025-01-12', 'PayPal'),
    ('24-0007', 3, 180.0, '2025-01-20', 'Bank Transfer');
