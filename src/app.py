from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from src.extension import db
from src.model import User, Athlete, TrainingPlan, Competition, AthleteTraining, Payment, AthleteCompetition
from datetime import datetime

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
            return render_template('login.html')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age')
        weight = request.form.get('weight')
        weight_category = request.form.get('weight_category')

        # Validate required fields
        if not name or not age or not weight or not weight_category:
            return jsonify({
                'success': False,
                'message': 'All fields are required'
            }), 400

        athlete_id = Athlete.generate_athlete_id()

        try:
            # Create athlete record
            athlete = Athlete(
                athlete_id=athlete_id,
                name=name,
                age=int(age),
                current_weight=float(weight),
                weight_category=weight_category
            )
            db.session.add(athlete)
            db.session.commit()

            # Create user record
            user = User(
                user_id=athlete_id,
                role='athlete',
                athlete_id=athlete_id
            )
            db.session.add(user)
            db.session.commit()

            flash(f'Registration successful! Your Athlete ID is: {athlete_id}', 'success')
            return jsonify({
                'success': True,
                'message': 'Registration successful',
                'athlete_id': athlete_id,
                'redirect_url': url_for('login')
            }), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': 'Registration failed. Please try again.'
            }), 500

    # GET request - return the registration page
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
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        session_type = request.form.get('session_type')
        print(f"Received session_type: {session_type}")

        if not session_type:
            return render_template('payment_session.html',
                                 athlete=athlete,
                                 training_plan=training_plan)

        valid_session_types = ['monthly', 'weekly', 'private']
        if session_type not in valid_session_types:
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
            return redirect(url_for('dashboard'))

        # Validate session_type
        valid_types = ['monthly', 'weekly', 'private']
        if session_type not in valid_types:
            print(f"Invalid session type: {session_type}")
            return redirect(url_for('payment_session_type',
                                  athlete_id=athlete_id,
                                  training_plan_id=plan_id))

        if request.method == 'POST':
            payment_method = request.form.get('payment_method')

            if not payment_method:
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
                    start_date=datetime.utcnow(),
                    end_date=None
                )
                db.session.add(new_training)

                db.session.commit()
                return redirect(url_for('dashboard'))  # Successful redirect
            except Exception as e:
                print(f"Error during payment processing: {str(e)}")  # Log the error
                db.session.rollback()
                return redirect(url_for('payment_method', athlete_id=athlete_id, plan_id=training_plan.training_plan_id,
                                        session_type=session_type))

        # GET request - show the payment method form
        return render_template('payment_method.html',
                            athlete=athlete,
                            training_plan=training_plan,
                            session_type=session_type)

    except Exception as e:
        return redirect(url_for('dashboard'))


@app.route('/register_competition/<athlete_id>/<competition_id>', methods=['GET', 'POST'])
def register_competition(athlete_id, competition_id):
    athlete = Athlete.query.filter_by(athlete_id=athlete_id).first()
    competition = Competition.query.filter_by(competition_id=competition_id).first()

    if not athlete or not competition:
        return redirect(url_for('dashboard'))

    athlete_training = AthleteTraining.query.filter_by(athlete_id=athlete_id).first()
    if not athlete_training:
        return redirect(url_for('dashboard'))

    training_plan = TrainingPlan.query.filter_by(training_plan_id=athlete_training.training_plan_id).first()
    if training_plan and training_plan.category in ['intermediate', 'elite']:
        if request.method == 'POST':
            try:
                # Check if already registered
                existing_registration = AthleteCompetition.query.filter_by(
                    athlete_id=athlete_id,
                    competition_id=competition_id
                ).first()

                if existing_registration:
                    return redirect(url_for('dashboard'))

                # Create athlete competition registration
                athlete_competition = AthleteCompetition(
                    athlete_id=athlete_id,
                    competition_id=competition_id,
                    registration_date=datetime.utcnow()
                )
                db.session.add(athlete_competition)
                db.session.commit()

                return redirect(url_for('dashboard'))
            except Exception as e:
                db.session.rollback()
                print(f"Error during registration: {str(e)}")  # Print the actual error
                return render_template('competition_registration.html', athlete=athlete, competition=competition)

        return render_template('competition_registration.html', athlete=athlete, competition=competition)

    return redirect(url_for('dashboard'))


@app.route('/cancel_training/<int:training_id>', methods=['POST'])
def cancel_training(training_id):
    # Check if it's an AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    athlete_training = AthleteTraining.query.filter_by(id=training_id).first()

    if not athlete_training:
        if is_ajax:
            return jsonify({'success': False, 'message': 'Training plan not found'}), 404
        return redirect(url_for('dashboard'))

    try:
        db.session.delete(athlete_training)
        db.session.commit()

        if is_ajax:
            return jsonify({'success': True, 'message': 'Training plan cancelled successfully'})
        return redirect(url_for('dashboard'))

    except Exception as e:
        db.session.rollback()
        if is_ajax:
            return jsonify({'success': False, 'message': str(e)}), 500
        return redirect(url_for('dashboard'))


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get('role') != 'admin':
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

        # With cascade delete in models, just delete the athlete
        db.session.delete(athlete)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Athlete and all related records deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

# Training Plans routes
@app.route('/admin/plans/add', methods=['POST'])
@admin_required
def add_plan():
    try:
        required_fields = ['plan_name', 'monthly_fee', 'weekly_fee', 'private_hourly_fee', 'category', 'session_per_week']
        for field in required_fields:
            if field not in request.form:
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400

        plan = TrainingPlan(
            plan_name=request.form['plan_name'],
            description=request.form.get('description', ''),  # Optional field
            monthly_fee=float(request.form['monthly_fee']),
            weekly_fee=float(request.form['weekly_fee']),
            private_hourly_fee=float(request.form['private_hourly_fee']),
            category=request.form['category'],
            session_per_week=int(request.form['session_per_week'])
        )
        db.session.add(plan)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Plan added successfully',
            'plan': {
                'id': plan.training_plan_id,
                'name': plan.plan_name,
                'category': plan.category,
                'monthly_fee': plan.monthly_fee
            }
        })
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Invalid numeric value provided'}), 400
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
        return jsonify({'success': True, 'message': 'Plan and all related records deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400


# Competitions routes
@app.route('/admin/competitions/add', methods=['POST'])
@admin_required
def add_competition():
    try:
        # Validate required fields
        required_fields = ['competition_name', 'location', 'date', 'entry_fee', 'weight_category']
        for field in required_fields:
            if field not in request.form:
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400

        # Parse date string to datetime object
        try:
            competition_date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid date format. Use YYYY-MM-DD'}), 400

        competition = Competition(
            competition_name=request.form['competition_name'],
            location=request.form['location'],
            date=competition_date,
            entry_fee=float(request.form['entry_fee']),
            weight_category=request.form['weight_category']
        )
        db.session.add(competition)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Competition added successfully',
            'competition': {
                'id': competition.competition_id,
                'name': competition.competition_name,
                'date': competition.date.strftime('%Y-%m-%d'),  # Changed from strptime to strftime
            }
        })
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Invalid numeric value provided'}), 400
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
        return jsonify({'success': True, 'message': 'Competition and all related records deleted successfully'})
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