from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from src.extension import db
from src.model import User, Athlete, TrainingPlan, Competition, AthleteTraining, Payment
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
            session['role'] = athlete_data['role'].lower()

            # Redirect based on the role
            if athlete_data['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif athlete_data['role'] == 'athlete':
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

        # Debugging: Print out the form data
        print(f"Name: {name}, Age: {age}, Weight: {weight}, Category: {weight_category}")

        if not name or not age or not weight or not weight_category:
            flash("All fields are required.", "error")
            return render_template('register.html')

        # Generate unique athlete_id
        athlete_id = Athlete.generate_athlete_id()

        try:
            athlete = Athlete(athlete_id=athlete_id, name=name, age=int(age), current_weight=float(weight), weight_category=weight_category)
            db.session.add(athlete)
            db.session.commit()

            # Add user to users table
            user = User(user_id=athlete_id, role='athlete', athlete_id=athlete_id)
            db.session.add(user)
            db.session.commit()

            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()  # Rollback on error
            flash(f"Error during registration: {e}", "error")
            return render_template('register.html')

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    athlete_id = session.get('athlete_id')
    if not athlete_id:
        return redirect(url_for('login'))

    athlete = Athlete.query.filter_by(athlete_id=athlete_id).first()
    if not athlete:
        return redirect(url_for('login'))

    # Fetch all athletes, training plans, and competitions
    athletes = Athlete.query.all()
    plans = TrainingPlan.query.all()
    competitions = Competition.query.all()

    return render_template(
        'dashboard.html',
        athlete=athlete,
        athletes=athletes,
        plans=plans,
        competitions=competitions
    )
@app.route('/register_plan', methods=['POST'])
def register_plan():
    # Get the data from the request
    data = request.get_json()
    athlete_id = data.get('athlete_id')  # Athlete's ID, passed from the frontend
    plan_name = data.get('plan_name')  # Plan name (e.g., 'Monthly Plan', 'Weekly Plan', 'Private Plan')
    session_type = data.get('session_type')  # e.g., 'monthly', 'weekly', 'private'
    payment_method = data.get('payment_method')  # Payment method (e.g., 'credit', 'paypal', etc.)

    # Validate input data
    if not athlete_id or not plan_name or not session_type or not payment_method:
        return jsonify({"success": False, "message": "All fields are required."})

    # Fetch the training plan by name
    training_plan = TrainingPlan.query.filter_by(plan_name=plan_name).first()
    if not training_plan:
        return jsonify({"success": False, "message": "Training plan not found."})

    # Calculate the amount based on the session type
    if session_type == 'monthly':
        amount = training_plan.monthly_fee
    elif session_type == 'weekly':
        amount = training_plan.weekly_fee
    elif session_type == 'private':
        amount = training_plan.private_hourly_fee
    else:
        return jsonify({"success": False, "message": "Invalid session type."})

    try:
        # Create a new Payment record
        new_payment = Payment(
            athlete_id=athlete_id,
            training_plan_id=training_plan.training_plan_id,
            amount=amount,
            payment_method=payment_method,
            plan_type=session_type
        )
        db.session.add(new_payment)

        # Create an AthleteTraining record to track the athlete's registration to the plan
        new_training = AthleteTraining(
            athlete_id=athlete_id,
            training_plan_id=training_plan.training_plan_id,
            start_date=datetime.datetime.utcnow(),  # Current date as the start date
            end_date=None  # Assuming this is an ongoing training session
        )
        db.session.add(new_training)

        # Commit both Payment and AthleteTraining to the database
        db.session.commit()

        return jsonify({"success": True, "message": "Successfully registered for the plan and payment recorded!"})
    except Exception as e:
        # Rollback the transaction in case of an error
        db.session.rollback()
        return jsonify({"success": False, "message": f"Error: {str(e)}"})

# Admin Dashboard Route
@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
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
        new_user = User(user_id=f"guest-{int(datetime.datetime.now().timestamp())}", role="guest")
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
