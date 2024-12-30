from flask import Blueprint, session, redirect, url_for, render_template

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def athlete_dashboard():
    if 'user_id' not in session or session.get('role') != 'Athlete':
        return redirect(url_for('login.login'))
    return render_template('dashboard.html')

@dashboard_bp.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'Admin':
        return redirect(url_for('login.login'))
    return "Admin Dashboard"

@dashboard_bp.route('/guest_dashboard')
def guest_dashboard():
    return "Guest Dashboard"
