-- Insert data into athletes table
INSERT INTO athletes (athlete_id, name, age, current_weight, weight_category) VALUES
('23-0001', 'John Smith', 25, 70.5, 'Lightweight'),
('23-0002', 'Mary Johnson', 22, 65.0, 'Lightweight'),
('23-0003', 'Mike Brown', 28, 90.2, 'Heavyweight');

-- Insert data into training_plans table
INSERT INTO training_plans (plan_name, description, monthly_fee) VALUES
('Beginner Plan', 'Basic training for new athletes', 50.00),
('Advanced Plan', 'Advanced techniques for seasoned players', 100.00),
('Weight Training', 'Focus on weight category improvements', 75.00);

-- Insert data into athlete_training table
INSERT INTO athlete_training (athlete_id, training_plan_id, start_date, end_date) VALUES
('23-0001', 1, '2024-01-01', '2024-03-01'),
('23-0002', 2, '2024-02-15', NULL),
('23-0003', 3, '2024-01-10', '2024-04-10');

-- Insert data into competition table
INSERT INTO competition (competition_name, date, location) VALUES
('Regional Judo Cup', '2024-05-10', 'New York, USA'),
('State Finals', '2024-06-20', 'Los Angeles, CA'),
('National Open', '2024-08-15', 'Chicago, IL');

-- Insert data into athlete_competition table
INSERT INTO athlete_competition (athlete_id, competition_id, registration_date) VALUES
('23-0001', 1, '2024-04-01'),
('23-0002', 2, '2024-05-15'),
('23-0003', 3, '2024-06-01');

-- Insert data into payments table
INSERT INTO payments (athlete_id, training_plan_id, amount, payment_date) VALUES
('23-0001', 1, 50.00, '2024-01-01'),
('23-0002', 2, 100.00, '2024-02-15'),
('23-0003', 3, 75.00, '2024-01-10');

-- Insert data into users table
INSERT INTO users (role, athlete_id) VALUES
('athlete', '23-0001'),
('athlete', '23-0002'),
('athlete', '23-0003'),
('guest', NULL);
