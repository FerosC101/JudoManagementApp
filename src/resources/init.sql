-- Create Enum for plan_type
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'plan_type_enum') THEN
        CREATE TYPE plan_type_enum AS ENUM ('monthly', 'weekly', 'private');
    END IF;
END $$;

-- Create athletes table
CREATE TABLE IF NOT EXISTS athletes (
    athlete_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INTEGER NOT NULL,
    current_weight FLOAT NOT NULL,
    weight_category VARCHAR(20)
);

-- Create training_plans table
CREATE TABLE IF NOT EXISTS training_plans (
    training_plan_id SERIAL PRIMARY KEY, -- Auto-incrementing ID
    plan_name VARCHAR(50) NOT NULL, -- Name of the training plan
    description TEXT, -- Description of the plan (optional)
    monthly_fee FLOAT NOT NULL, -- Monthly fee for the plan
    weekly_fee FLOAT, -- Weekly fee for the plan (optional)
    private_hourly_fee FLOAT, -- Private hourly fee for the plan (optional)
    category VARCHAR(20) NOT NULL, -- Category of the plan
    session_per_week INTEGER -- Number of sessions per week (optional)
);

-- Create competitions table
CREATE TABLE IF NOT EXISTS competitions (
    competition_id SERIAL PRIMARY KEY,
    competition_name VARCHAR(50) NOT NULL,
    location VARCHAR(100),
    date DATE,
    weight_category VARCHAR(20) NOT NULL,
    entry_fee FLOAT NOT NULL
);

-- Create payments table
CREATE TABLE IF NOT EXISTS payments (
    payment_id SERIAL PRIMARY KEY,
    athlete_id VARCHAR(10) NOT NULL,
    training_plan_id INTEGER NOT NULL,
    amount FLOAT NOT NULL,
    payment_date DATE DEFAULT CURRENT_DATE NOT NULL,
    payment_method VARCHAR(20) NOT NULL,
    plan_type plan_type_enum NOT NULL,
    CONSTRAINT fk_payments_athletes FOREIGN KEY (athlete_id) REFERENCES athletes (athlete_id) ON DELETE CASCADE,
    CONSTRAINT fk_payments_training_plans FOREIGN KEY (training_plan_id) REFERENCES training_plans (training_plan_id) ON DELETE CASCADE
);

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(20) PRIMARY KEY,
    role VARCHAR(50) NOT NULL,
    athlete_id VARCHAR(10) UNIQUE,
    CONSTRAINT fk_users_athletes FOREIGN KEY (athlete_id) REFERENCES athletes (athlete_id) ON DELETE CASCADE,
    CONSTRAINT check_role CHECK (role IN ('athlete', 'guest'))
);

-- Create athlete_competitions table
CREATE TABLE IF NOT EXISTS athlete_competitions (
    id SERIAL PRIMARY KEY,
    athlete_id VARCHAR(10) NOT NULL,
    competition_id INTEGER NOT NULL,
    registration_date DATE NOT NULL,
    CONSTRAINT fk_athlete_competitions_athletes FOREIGN KEY (athlete_id) REFERENCES athletes (athlete_id) ON DELETE CASCADE,
    CONSTRAINT fk_athlete_competitions_competitions FOREIGN KEY (competition_id) REFERENCES competitions (competition_id) ON DELETE CASCADE
);

-- Create athlete_training table
CREATE TABLE IF NOT EXISTS athlete_training (
    id SERIAL PRIMARY KEY,
    athlete_id VARCHAR(10) NOT NULL,
    training_plan_id INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    CONSTRAINT fk_athlete_training_athletes FOREIGN KEY (athlete_id) REFERENCES athletes (athlete_id) ON DELETE CASCADE,
    CONSTRAINT fk_athlete_training_training_plans FOREIGN KEY (training_plan_id) REFERENCES training_plans (training_plan_id) ON DELETE CASCADE
);

