from datetime import datetime
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(UserMixin, db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(200),
        nullable=False
    )

    user_type = db.Column(
        db.String(20),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def __repr__(self):

        return f'<User {self.username}>'


class Child(db.Model):

    __tablename__ = 'children'

    id = db.Column(db.Integer, primary_key=True)

    parent_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id')
    )

    child_user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id')
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


class WebActivity(db.Model):

    __tablename__ = 'web_activities'

    id = db.Column(db.Integer, primary_key=True)

    child_id = db.Column(db.Integer)

    website = db.Column(db.String(300))

    category = db.Column(db.String(100))

    timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


class Alert(db.Model):

    __tablename__ = 'alerts'

    id = db.Column(db.Integer, primary_key=True)

    child_name = db.Column(db.String(100))

    message = db.Column(db.String(500))

    alert_type = db.Column(db.String(100))

    timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    is_read = db.Column(
        db.Boolean,
        default=False
    )

    def __repr__(self):

        return f'<Alert {self.alert_type}>'