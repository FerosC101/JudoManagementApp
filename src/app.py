from flask import Flask, render_template, request, redirect, url_for, session, flash
from src.extension import db
from src.model import User, Athlete, AthleteTraining, AthleteCompetition, Payment, TrainingPlan, Competition
import datetime

app = Flask(__name__, template_folder='templates')
app.config.from_object('config.Config')
app.secret_key = 'sigma'
db.init_app(app)

# Home Route
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        athlete_id = request.form.get('athlete_id')

        if not athlete_id:
            flash("Athlete ID cannot be empty. Please try again.", "error")
            return render_template('login.html')

        athlete_id = athlete_id.strip()

        # Fetch the athlete and role using the updated function
        athlete_data = get_athlete_by_id(athlete_id)

        if athlete_data:
            session['athlete_id'] = athlete_data['athlete'].athlete_id
            session['role'] = athlete_data['role'].lower()  # Make sure the role is stored in lowercase

            print(f"Role: {athlete_data['role']}")  # Debugging

            # Redirect based on the role
            if athlete_data['role'] == 'admin':  # Make sure this matches the stored role in lowercase
                return redirect(url_for('admin_dashboard'))
            elif athlete_data['role'] == 'athlete':  # Make sure this matches the stored role in lowercase
                return redirect(url_for('dashboard'))
            else:
                return redirect(url_for('guest_view'))
        else:
            flash("Invalid Athlete ID. Please try again or register.", "error")
            return render_template('login.html')

    return render_template('login.html')


# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age')
        weight = request.form.get('weight')
        weight_category = request.form.get('weight_category')

        if not name or not age or not weight:
            flash("All fields are required.", "error")
            return render_template('register.html')

        athlete_id = Athlete.generate_athlete_id()

        athlete = Athlete(athlete_id=athlete_id, name=name, age=int(age), current_weight=float(weight), weight_category=weight_category)
        db.session.add(athlete)
        db.session.commit()

        # Add user to users table
        user = User(user_id=athlete_id, role='athlete', athlete_id=athlete_id)
        db.session.add(user)
        db.session.commit()

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

# Athlete Dashboard Route
@app.route('/dashboard')
def dashboard():
    athlete_id = session.get('athlete_id')
    if not athlete_id:
        return redirect(url_for('login'))  # Ensure athlete is logged in

    athlete = Athlete.query.filter_by(athlete_id=athlete_id).first()
    if not athlete:
        return redirect(url_for('login'))  # Handle non-existent athlete

    # Fetch related data
    athletes = Athlete.query.all()
    plans = TrainingPlan.query.all()
    competitions = AthleteCompetition.query.all()


    # Debugging output for the fetched data
    print(f"athlete: {athletes}")
    print(f"Competitions: {competitions}")
    print(f"TrainingPlan: {plans}")

    return render_template('dashboard.html', athletes=athletes, plans=plans, competitions=competitions)



# Admin Dashboard Route
@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':  # Ensure you're checking for 'admin' in lowercase
        flash("Access denied.", "error")
        return redirect(url_for('login'))
    return render_template('admin_dashboard.html')

# Guest View Route
@app.route('/guest_view')
def guest_view():
    athletes = Athlete.query.all()
    return render_template('guest_view.html', athletes=athletes)

# Guest Registration
@app.route('/guest_register', methods=['POST'])
def guest_register():
    try:
        new_user = User(user_id=f"guest-{int(datetime.datetime.now().timestamp())}", role="Guest")
        db.session.add(new_user)
        db.session.commit()
        flash("Guest registration successful!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {e}", "error")
    return redirect(url_for('login'))

def get_athlete_by_id(athlete_id):
    """
    Retrieves an athlete and their role from the database by athlete_id.

    Parameters:
        athlete_id (str): The athlete ID to search for (e.g., '23-0001').

    Returns:
        dict: A dictionary containing athlete and role information if found,
              None if not found.
    """
    athlete = Athlete.query.filter_by(athlete_id=athlete_id).first()
    if athlete:
        role = User.query.filter_by(user_id=athlete_id).first()
        return {'athlete': athlete, 'role': role.role} if role else None
    return None

if __name__ == '__main__':
    app.run(debug=True)
