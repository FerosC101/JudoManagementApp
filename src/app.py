from flask import Flask, render_template, request, redirect, url_for, session, flash
from src.extension import db
from src.model import Users, Athlete

app = Flask(__name__, template_folder='templates')
app.config.from_object('config.Config')

db.init_app(app)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        print(f"User ID entered: {user_id}")  # Debug statement

        user = Users.query.filter_by(user_id=user_id).first()
        print(f"User fetched: {user}")  # Debug statement

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
            flash("Invalid User ID. Please try again or create a new account.", "error")
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age')
        current_weight = request.form.get('current_weight')
        weight_category = request.form.get('weight_category')
        role = request.form.get('role')

        new_athlete = Athlete(
            name=name,
            age=int(age),
            current_weight=float(current_weight),
            weight_category=weight_category
        )
        db.session.add(new_athlete)
        db.session.commit()

        new_user = Users(
            role=role,
            athlete_id=new_athlete.athlete_id
        )
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/guest')
def guest_view():
    athletes = Athlete.query.all()
    return render_template('guest_view.html', athletes=athletes)

if __name__ == "__main__":
    app.run(debug=True)
