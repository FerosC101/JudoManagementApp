from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from src.model import Users

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        user = Users.query.filter_by(user_id=user_id).first()

        if user:
            session['user_id'] = user.user_id
            session['role'] = user.role
            if user.role == 'Admin':
                return redirect(url_for('dashboard.admin_dashboard'))
            elif user.role == 'Athlete':
                return redirect(url_for('dashboard.athlete_dashboard'))
            else:
                return redirect(url_for('dashboard.guest_dashboard'))
        else:
            flash("Invalid User ID. Please try again.", "error")
            return redirect(url_for('login.login'))
    return render_template('login.html')
