import os
from datetime import datetime

from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user
)
from flask_socketio import SocketIO
from werkzeug.security import generate_password_hash, check_password_hash


# ---------------- APP SETUP ----------------

app = Flask(__name__)

app.config['SECRET_KEY'] = 'kidguard-secret'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kidguard.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

socketio = SocketIO(app)

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = 'login'


# ---------------- DATABASE MODELS ----------------

class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), unique=True)

    email = db.Column(db.String(100), unique=True)

    password_hash = db.Column(db.String(200))

    user_type = db.Column(db.String(20))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Alert(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    message = db.Column(db.String(500))

    alert_type = db.Column(db.String(100))

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# ---------------- LOGIN MANAGER ----------------

@login_manager.user_loader
def load_user(user_id):

    return User.query.get(int(user_id))


# ---------------- ROUTES ----------------

@app.route('/')
def home():

    return render_template('home.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'POST':

        username = request.form.get('username')

        email = request.form.get('email')

        password = request.form.get('password')

        user_type = request.form.get('user_type')

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:

            flash('Username already exists')

            return redirect(url_for('signup'))

        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            user_type=user_type
        )

        db.session.add(new_user)

        db.session.commit()

        flash('Account created successfully')

        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form.get('username')

        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):

            login_user(user)

            if user.user_type == 'parent':

                return redirect(url_for('parent_dashboard'))

            else:

                return redirect(url_for('child_dashboard'))

        flash('Invalid username or password')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():

    logout_user()

    flash('Logged out successfully')

    return redirect(url_for('home'))


@app.route('/parent_dashboard')
@login_required
def parent_dashboard():

    alerts = Alert.query.order_by(Alert.timestamp.desc()).all()

    return render_template(
        'parent_dashboard.html',
        alerts=alerts
    )


@app.route('/child_dashboard')
@login_required
def child_dashboard():

    return render_template('child_dashboard.html')


# ---------------- MAIN ----------------

if __name__ == '__main__':

    with app.app_context():

        db.create_all()

    socketio.run(app, debug=True)