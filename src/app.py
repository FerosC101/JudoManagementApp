from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from src.extension import db
from src.model import User, Athlete, TrainingPlan, Competition, AthleteTraining, Payment, AthleteCompetition
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
    if request.args.get('guest') == 'true':
        session['role'] = 'guest'
        return redirect(url_for('guest_view'))

    if request.method == 'POST':
        athlete_id = request.form.get('athlete_id')

        if not athlete_id:
            flash("Athlete ID cannot be empty. Please try again.", "error")
            return render_template('login.html')

        athlete_id = athlete_id.strip()

        # Check for specific admin ID
        if athlete_id == '428912':
            session['athlete_id'] = athlete_id
            session['role'] = 'admin'
            return redirect(url_for('admin_dashboard'))

        # Fetch athlete data from the database
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

        athlete_id = Athlete.generate_athlete_id()

        try:
            athlete = Athlete(athlete_id=athlete_id, name=name, age=int(age), current_weight=float(weight), weight_category=weight_category)
            db.session.add(athlete)
            db.session.commit()

            user = User(user_id=athlete_id, role='athlete', athlete_id=athlete_id)
            db.session.add(user)
            db.session.commit()

            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error during registration: {e}", "error")
            return render_template('register.html')

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    athlete_id = session.get('athlete_id')
    if not athlete_id:
        return redirect(url_for('login'))

    athlete_id = str(athlete_id)

    athlete = Athlete.query.filter_by(athlete_id=athlete_id).first()
    if not athlete:
        return redirect(url_for('login'))

    athletes = Athlete.query.all()
    plans = TrainingPlan.query.all()
    competitions = Competition.query.all()

    return render_template(
        'dashboard.html',
        athlete=athlete,
        athletes=athletes,
        plans=plans,
        competitions=competitions,
        athlete_id=athlete_id  # Explicitly pass the athlete_id
    )


@app.route('/payment_session_type/<athlete_id>/<training_plan_id>', methods=['GET', 'POST'])
def payment_session_type(athlete_id, training_plan_id):
    print(f"Attempting to access payment session for athlete_id: {athlete_id}, training_plan_id: {training_plan_id}")

    athlete = Athlete.query.filter_by(athlete_id=athlete_id).first()
    training_plan = TrainingPlan.query.filter_by(training_plan_id=training_plan_id).first()

    if not athlete or not training_plan:
        flash("Invalid athlete or training plan.", "error")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        session_type = request.form.get('session_type')
        print(f"Received session_type: {session_type}")

        if not session_type:
            flash("Session type is required.", "error")
            return render_template('payment_session.html',
                                 athlete=athlete,
                                 training_plan=training_plan)

        valid_session_types = ['monthly', 'weekly', 'private']
        if session_type not in valid_session_types:
            flash("Invalid session type selected.", "error")
            return render_template('payment_session.html',
                                 athlete=athlete,
                                 training_plan=training_plan)

        try:
            # Make sure we're passing the correct parameter names
            return redirect(url_for('payment_method',
                                  athlete_id=athlete_id,
                                  plan_id=training_plan_id,  # Changed from training_plan_id to plan_id
                                  session_type=session_type))
        except Exception as e:
            print(f"Error in redirect: {str(e)}")
            flash(f"Error in redirect: {str(e)}", "error")
            return render_template('payment_session.html',
                                 athlete=athlete,
                                 training_plan=training_plan)

    # GET request - just show the form
    return render_template('payment_session.html',
                         athlete=athlete,
                         training_plan=training_plan)

@app.route('/payment_method/<athlete_id>/<plan_id>/<session_type>', methods=['GET', 'POST'])
def payment_method(athlete_id, plan_id, session_type):
    try:
        print(f"Payment method route accessed with: athlete_id={athlete_id}, plan_id={plan_id}, session_type={session_type}")

        athlete = Athlete.query.filter_by(athlete_id=athlete_id).first()
        training_plan = TrainingPlan.query.filter_by(training_plan_id=plan_id).first()

        print(f"Athlete: {athlete}, Training Plan: {training_plan}")
        print(f"Session Type received: '{session_type}'")

        if not athlete or not training_plan:
            flash("Invalid athlete or training plan.", "error")
            return redirect(url_for('dashboard'))

        # Validate session_type
        valid_types = ['monthly', 'weekly', 'private']
        if session_type not in valid_types:
            print(f"Invalid session type: {session_type}")
            flash("Invalid session type.", "error")
            return redirect(url_for('payment_session_type',
                                  athlete_id=athlete_id,
                                  training_plan_id=plan_id))

        if request.method == 'POST':
            payment_method = request.form.get('payment_method')

            if not payment_method:
                flash("Payment method is required.", "error")
                return render_template('payment_method.html',
                                    athlete=athlete,
                                    training_plan=training_plan,
                                    session_type=session_type)

            # Calculate amount based on session type
            amount = {
                'monthly': training_plan.monthly_fee,
                'weekly': training_plan.weekly_fee,
                'private': training_plan.private_hourly_fee
            }.get(session_type)

            try:
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

            except Exception as e:
                db.session.rollback()
                flash(f"Error processing payment: {str(e)}", "error")
                return render_template('payment_method.html',
                                    athlete=athlete,
                                    training_plan=training_plan,
                                    session_type=session_type)

        # GET request - show the payment method form
        return render_template('payment_method.html',
                            athlete=athlete,
                            training_plan=training_plan,
                            session_type=session_type)

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('dashboard'))


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
    if training_plan and training_plan.category in ['Intermediate', 'Elite']:
        if request.method == 'POST':
            try:
                # Check if already registered
                existing_registration = AthleteCompetition.query.filter_by(
                    athlete_id=athlete_id,
                    competition_id=competition_id
                ).first()

                if existing_registration:
                    flash("You are already registered for this competition.", "error")
                    return redirect(url_for('dashboard'))

                # Create athlete competition registration
                athlete_competition = AthleteCompetition(
                    athlete_id=athlete_id,
                    competition_id=competition_id,
                    registration_date=datetime.datetime.utcnow()
                )
                db.session.add(athlete_competition)
                db.session.commit()

                flash("Competition registration successful!", "success")
                return redirect(url_for('dashboard'))
            except Exception as e:
                db.session.rollback()
                print(f"Error during registration: {str(e)}")  # Print the actual error
                flash(f"Registration error: {str(e)}", "error")
                return render_template('competition_registration.html', athlete=athlete, competition=competition)

        return render_template('competition_registration.html', athlete=athlete, competition=competition)

    flash("You must be enrolled in an intermediate or elite plan to register for competitions.", "error")
    return redirect(url_for('dashboard'))


@app.route('/cancel_training/<int:training_id>', methods=['POST'])
def cancel_training(training_id):
    # Check if it's an AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    athlete_training = AthleteTraining.query.filter_by(id=training_id).first()

    if not athlete_training:
        if is_ajax:
            return jsonify({'success': False, 'message': 'Training plan not found'}), 404
        flash('Training plan not found.', 'error')
        return redirect(url_for('dashboard'))

    try:
        db.session.delete(athlete_training)
        db.session.commit()

        if is_ajax:
            return jsonify({'success': True, 'message': 'Training plan cancelled successfully'})
        flash('Training plan cancelled successfully.', 'success')
        return redirect(url_for('dashboard'))

    except Exception as e:
        db.session.rollback()
        if is_ajax:
            return jsonify({'success': False, 'message': str(e)}), 500
        flash(f'Error cancelling training plan: {str(e)}', 'error')
        return redirect(url_for('dashboard'))


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get('role') != 'admin':
            flash("Access denied.", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

@app.route('/admin_dashboard')
@admin_required
def admin_dashboard():
    athletes = Athlete.query.all()
    plans = TrainingPlan.query.all()
    competitions = Competition.query.all()
    return render_template('admin_dashboard.html',
                           athletes=athletes,
                           plans=plans,
                           competitions=competitions)


# Athletes routes
@app.route('/admin/athletes/delete/<athlete_id>', methods=['POST'])
@admin_required
def delete_athlete(athlete_id):
    try:
        athlete = Athlete.query.filter_by(athlete_id=athlete_id).first()
        if not athlete:
            return jsonify({'success': False, 'message': 'Athlete not found'}), 404

        db.session.delete(athlete)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Athlete deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

# Training Plans routes
@app.route('/admin/plans/add', methods=['POST'])
@admin_required
def add_plan():
    try:
        plan = TrainingPlan(
            plan_name=request.form['plan_name'],
            description=request.form['description'],
            monthly_fee=float(request.form['monthly_fee']),
            weekly_fee=float(request.form['weekly_fee']),
            private_hourly_fee=float(request.form['private_hourly_fee']),
            category=request.form['category'],
            session_per_week=int(request.form['session_per_week'])
        )
        db.session.add(plan)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Plan added successfully', 'plan': {
            'id': plan.training_plan_id,
            'name': plan.plan_name
        }})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400


@app.route('/admin/plans/edit/<training_plan_id>', methods=['PUT'])
@admin_required
def edit_plan(training_plan_id):
    try:
        plan = TrainingPlan.query.filter_by(training_plan_id=training_plan_id).first()
        if not plan:
            return jsonify({'success': False, 'message': 'Plan not found'}), 404

        plan.plan_name = request.form['plan_name']
        plan.description = request.form['description']
        plan.monthly_fee = float(request.form['monthly_fee'])
        plan.weekly_fee = float(request.form['weekly_fee'])
        plan.private_hourly_fee = float(request.form['private_hourly_fee'])
        plan.category = request.form['category']
        plan.session_per_week = int(request.form['session_per_week'])

        db.session.commit()
        return jsonify({'success': True, 'message': 'Plan updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400


@app.route('/admin/plans/delete/<training_plan_id>', methods=['POST'])
@admin_required
def delete_plan(training_plan_id):
    try:
        plan = TrainingPlan.query.filter_by(training_plan_id=training_plan_id).first()
        if not plan:
            return jsonify({'success': False, 'message': 'Plan not found'}), 404

        db.session.delete(plan)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Plan deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400


# Competitions routes
@app.route('/admin/competitions/add', methods=['POST'])
@admin_required
def add_competition():
    try:
        competition = Competition(
            competition_name=request.form['competition_name'],
            location=request.form['location'],
            date=datetime.strptime(request.form['date'], '%Y-%m-%d'),
            entry_fee=float(request.form['entry_fee']),
            weight_category=request.form['weight_category']
        )
        db.session.add(competition)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Competition added successfully', 'competition': {
            'id': competition.competition_id,
            'name': competition.competition_name
        }})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400


@app.route('/admin/competitions/edit/<competition_id>', methods=['PUT'])
@admin_required
def edit_competition(competition_id):
    try:
        competition = Competition.query.filter_by(competition_id=competition_id).first()
        if not competition:
            return jsonify({'success': False, 'message': 'Competition not found'}), 404

        competition.competition_name = request.form['competition_name']
        competition.location = request.form['location']
        competition.date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        competition.entry_fee = float(request.form['entry_fee'])
        competition.weight_category = request.form['weight_category']

        db.session.commit()
        return jsonify({'success': True, 'message': 'Competition updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400


@app.route('/admin/competitions/delete/<competition_id>', methods=['POST'])
@admin_required
def delete_competition(competition_id):
    try:
        competition = Competition.query.filter_by(competition_id=competition_id).first()
        if not competition:
            return jsonify({'success': False, 'message': 'Competition not found'}), 404

        db.session.delete(competition)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Competition deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/guest_view')
def guest_view():
    # Query all necessary data
    athletes = Athlete.query.all()
    plans = TrainingPlan.query.all()
    competitions = Competition.query.all()

    return render_template(
        'guest_view.html',
        athletes=athletes,
        plans=plans,
        competitions=competitions
    )

def get_athlete_by_id(athlete_id):
    athlete = Athlete.query.filter_by(athlete_id=athlete_id).first()
    if athlete:
        role = User.query.filter_by(user_id=athlete_id).first()
        return {'athlete': athlete, 'role': role.role} if role else None
    return None

if __name__ == '__main__':
    app.run(debug=True)