from flask import Flask, render_template, request, redirect, url_for, session, flash
from src.extension import db
from src.model import User, Athlete
import datetime

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
        # Debugging: Check form data
        print(request.form)

        athlete_id = request.form.get('athlete_id')
        if not athlete_id:
            flash("Athlete ID cannot be empty. Please try again.", "error")
            return render_template('login.html')

        athlete_id = athlete_id.strip()

        # Fetch the athlete using the function
        athlete = get_athlete_by_id(athlete_id)

        if athlete:
            session['athlete_id'] = athlete.athlete_id  # Store athlete ID in session
            session['role'] = athlete.role  # Assuming the role is stored in the Athlete model

            # Redirect based on the role
            if athlete.role == 'Admin':
                return redirect(url_for('admin_dashboard'))
            elif athlete.role == 'Athlete':
                return redirect(url_for('dashboard'))
            else:
                return redirect(url_for('guest_view'))
        else:
            flash("Invalid Athlete ID. Please try again or register.", "error")

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
            flash('All fields are required!', 'error')
            return redirect(url_for('register'))

        try:
            # Generate athlete_id
            athlete_id = f"{datetime.datetime.now().year}-{Athlete.query.count() + 1:04d}"

            # Create Athlete
            new_athlete = Athlete(
                athlete_id=athlete_id,
                name=name,
                age=int(age),
                current_weight=float(weight),
                weight_category=weight_category
            )
            db.session.add(new_athlete)
            db.session.commit()

            # Create User (athlete role)
            new_user = User(user_id=athlete_id, role='Athlete', athlete_id=athlete_id)
            db.session.add(new_user)
            db.session.commit()

            flash(f"Registration successful! Your athlete ID is {athlete_id}.", 'success')
            return redirect(url_for('login'))

        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", 'error')
            return redirect(url_for('register'))

    return render_template('register.html')

# Dashboard Route
@app.route('/dashboard')
def dashboard():
    if session.get('role') != 'Athlete':
        return redirect(url_for('login'))
    return render_template('dashboard.html')

# Admin Dashboard Route
@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('role') != 'Admin':
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
    Retrieves an athlete from the database by athlete_id (string).

    Parameters:
        athlete_id (str): The athlete ID to search for (e.g., '23-0001').

    Returns:
        Athlete object if found, None otherwise.
    """
    try:
        # Query the database for the athlete
        athlete = Athlete.query.filter_by(athlete_id=athlete_id).first()

        if athlete:
            return athlete  # Return the Athlete object if found
        else:
            flash("Invalid Athlete ID. Please try again or register.", "error")
            return None

    except Exception as e:
        flash(f"An error occurred while retrieving the athlete: {str(e)}", "error")
        return None


# Run Application
if __name__ == "__main__":
    app.run(debug=True)
