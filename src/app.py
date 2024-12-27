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
        user = Users.query.filter_by(user_id=user_id).first()

        if user:
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'user':
                return redirect(url_for('user_dashboard', athlete_id=user.athlete_id))
        else:
            flash("User ID not found. Please try again or create an account.", "error")

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age')
        current_weight = request.form.get('current_weight')
        weight_category = request.form.get('weight_category')
        role = request.form.get('role')  # 'user' or 'admin'

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
