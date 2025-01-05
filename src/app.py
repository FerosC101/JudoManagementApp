from flask import Flask, render_template, request, redirect, url_for, session, flash
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

    def generate_payment_url(training_plan_id):
        return url_for('payment_session_type', athlete_id=athlete_id, training_plan_id=training_plan_id)

    return render_template(
        'dashboard.html',
        athlete=athlete,
        athletes=athletes,
        plans=plans,
        competitions=competitions,
        athlete_id=athlete_id,  # Pass athlete_id to the template
        generate_payment_url=generate_payment_url
    )


@app.route('/payment_session_type/<athlete_id>/<training_plan_id>', methods=['GET', 'POST'])
def payment_session_type(athlete_id, training_plan_id):
    print(f"Attempting to access payment session for athlete_id: {athlete_id}, training_plan_id: {training_plan_id}")

    # Fetch the athlete and training plan based on their IDs
    athlete = Athlete.query.filter_by(athlete_id=athlete_id).first()
    training_plan = TrainingPlan.query.filter_by(training_plan_id=training_plan_id).first()

    if not athlete or not training_plan:
        flash("Invalid athlete or training plan.", "error")
        return redirect(url_for('dashboard'))

    # Handle the POST request
    if request.method == 'POST':
        # Get the session_type from the form
        session_type = request.form.get('session_type')
        if not session_type:
            flash("Session type is required.", "error")
            return render_template('payment_session.html', athlete=athlete, training_plan=training_plan)

        # Redirect to the payment method route with the correct parameters
        return redirect(
            url_for('payment_method', athlete_id=athlete_id, plan_id=training_plan_id, session_type=session_type)
        )

    # Handle the GET request
    return render_template('payment_session.html', athlete=athlete, training_plan=training_plan)

@app.route('/payment_method/<athlete_id>/<plan_id>/<session_type>', methods=['GET', 'POST'])
def payment_method(athlete_id, plan_id, session_type):
    # Fetch the athlete and training plan details
    athlete = Athlete.query.filter_by(athlete_id=athlete_id).first()
    training_plan = TrainingPlan.query.filter_by(training_plan_id=plan_id).first()

    if not athlete or not training_plan:
        flash("Invalid athlete or training plan.", "error")
        return redirect(url_for('dashboard'))

    # Validate session_type
    valid_types = ['monthly', 'weekly', 'private']
    if session_type not in valid_types:
        flash("Invalid session type.", "error")
        return redirect(url_for('payment_session_type', athlete_id=athlete_id, training_plan_id=plan_id))

    if request.method == 'POST':
        payment_method = request.form.get('payment_method')

        if not payment_method:
            flash("Payment method is required.", "error")
            return render_template('payment_method.html', athlete=athlete, training_plan=training_plan, session_type=session_type)

        # Calculate the amount based on session type
        amount = {
            'monthly': training_plan.monthly_fee,
            'weekly': training_plan.weekly_fee,
            'private': training_plan.private_hourly_fee
        }.get(session_type, 0)

        # Create the Payment and AthleteTraining records
        new_payment = Payment(
            athlete_id=athlete_id,
            training_plan_id=training_plan.training_plan_id,
            amount=amount,
            payment_method=payment_method,
            plan_type=session_type,
        )
        db.session.add(new_payment)

        new_training = AthleteTraining(
            athlete_id=athlete_id,
            training_plan_id=training_plan.training_plan_id,
            start_date=datetime.datetime.utcnow(),
            end_date=None
        )
        db.session.add(new_training)

        db.session.commit()

        flash("Payment successful and registration completed!", "success")
        return redirect(url_for('dashboard'))

    return render_template('payment_method.html', athlete=athlete, training_plan=training_plan, session_type=session_type)

@app.route('/register_competition/<athlete_id>/<competition_id>', methods=['GET', 'POST'])
def register_competition(athlete_id, competition_id):
    athlete = Athlete.query.filter_by(athlete_id=athlete_id).first()
    competition = Competition.query.filter_by(competition_id=competition_id).first()

    if not athlete or not competition:
        flash("Invalid athlete or competition.", "error")
        return redirect(url_for('dashboard'))

    athlete_training = AthleteTraining.query.filter_by(athlete_id=athlete_id).first()
    if not athlete_training:
        flash("You must be enrolled in a training plan to register for a competition.", "error")
        return redirect(url_for('dashboard'))

    training_plan = TrainingPlan.query.filter_by(training_plan_id=athlete_training.training_plan_id).first()
    if training_plan and training_plan.plan_level in ['intermediate', 'elite']:
        if request.method == 'POST':
            flash("Competition registration successful!", "success")
            return redirect(url_for('dashboard'))

        return render_template('register_competition.html', athlete=athlete, competition=competition)

    flash("You must be enrolled in an intermediate or elite plan to register for competitions.", "error")
    return redirect(url_for('dashboard'))

@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        flash("Access denied.", "error")
        return redirect(url_for('login'))
    return render_template('admin_dashboard.html')

@app.route('/guest_view')
def guest_view():
    athletes = Athlete.query.all()
    return render_template('guest_view.html', athletes=athletes)

def get_athlete_by_id(athlete_id):
    athlete = Athlete.query.filter_by(athlete_id=athlete_id).first()
    if athlete:
        role = User.query.filter_by(user_id=athlete_id).first()
        return {'athlete': athlete, 'role': role.role} if role else None
    return None

if __name__ == '__main__':
    app.run(debug=True)
