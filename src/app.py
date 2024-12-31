from flask import Flask, render_template, request, redirect, url_for, session, flash
from src.extension import db
from src.model import User, Athlete
from src.routes.athletes import AthleteService

app = Flask(__name__, template_folder='templates')
app.config.from_object('config.Config')
app.secret_key = 'sigma'
db.init_app(app)

# Home Route
@app.route('/')
def home():
    return render_template('login.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user_id')

        # Fetch user from database using AthleteService
        user = AthleteService.get_user_by_id(user_id)

        if user:
            session['user_id'] = user.user_id
            session['role'] = user.role

            if user.role == 'Admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'Athlete':
                return redirect(url_for('dashboard'))
            else:
                return redirect(url_for('guest_dashboard'))
        else:
            flash("User does not exist. Please check your User ID or register for a new account.", "error")
            return redirect(url_for('login'))
    return render_template('login.html')

# Register Route
# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name')
            age = request.form.get('age')
            current_weight = request.form.get('current_weight')
            weight_category = request.form.get('weight_category')

            # Validate input
            if not all([name, age, current_weight, weight_category]):
                flash("All fields are required!", "error")
                return redirect(url_for('register'))

            # Save athlete data to database
            new_athlete = Athlete(
                athlete_id=Athlete.generate_athlete_id(),  # Generate ID here
                name=name,
                age=int(age),
                current_weight=float(current_weight),
                weight_category=weight_category
            )

            # Add Athlete object to the session
            db.session.add(new_athlete)
            db.session.flush()  # Ensure the athlete is written to the DB and the ID is available

            # Create user with default 'Athlete' role
            new_user = User(
                role="Athlete",
                athlete_id=new_athlete.athlete_id  # Use the auto-generated athlete_id
            )
            db.session.add(new_user)
            db.session.commit()

            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for('login'))

        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred during registration: {e}", "error")
            return redirect(url_for('register'))

    return render_template('register.html')

# Dashboard Route
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

# Guest View Route
@app.route('/guest')
def guest_view():
    athletes = Athlete.query.all()
    return render_template('guest_view.html', athletes=athletes)

# Guest Registration Route
@app.route('/guest_register', methods=['POST'])
def guest_register():
    try:
        new_user = User(
            role='Guest',
            athlete_id=None  # No athlete ID for guest users
        )
        db.session.add(new_user)
        db.session.commit()

        flash("Guest registration successful! Please log in.", "success")
        return redirect(url_for('login'))

    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred: {e}", "error")
        return redirect(url_for('home'))

# Admin Dashboard Route
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'role' not in session or session['role'] != 'Admin':
        flash("Access denied. Admins only.", "error")
        return redirect(url_for('login'))
    return render_template('admin_dashboard.html')

# Submission for Athlete Registration
@app.route('/submit_registration', methods=['POST'])
def submit_registration():
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name')
            age = request.form.get('age')
            weight = request.form.get('weight')
            weight_category = request.form.get('weight_category')

            # Validate input
            if not all([name, age, weight, weight_category]):
                flash("All fields are required!", "error")
                return redirect(url_for('register'))

            # Save athlete data
            new_athlete = Athlete(
                name=name,
                age=int(age),
                current_weight=float(weight),
                weight_category=weight_category
            )
            db.session.add(new_athlete)
            db.session.commit()

            # Create user with default 'Athlete' role
            new_user = User(
                role='Athlete',
                athlete_id=new_athlete.athlete_id
            )
            db.session.add(new_user)
            db.session.commit()

            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('login'))

        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {e}", "error")
            return redirect(url_for('register'))
    return redirect(url_for('register'))

# Run Application
if __name__ == "__main__":
    app.run(debug=True)
