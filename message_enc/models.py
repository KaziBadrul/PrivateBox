from message_enc import db
from datetime import datetime
from flask_login import UserMixin
from message_enc import login_manager

@login_manager.user_loader
def login_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    rooms = db.relationship('UserRooms', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creator = db.Column(db.String(20), nullable=False, unique=False)
    title = db.Column(db.String(30), nullable=False, unique=False)
    description = db.Column(db.String(60), nullable=True, unique=False)
    key = db.Column(db.String(6), nullable=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    posts = db.relationship('Post', backref='on_room', lazy=True)

    def __repr__(self):
        return f"Room('{self.id}', '{self.title}', '{self.description}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False, unique=False)
    content = db.Column(db.String(60), nullable=False, unique=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)

class UserRooms(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    room_id = db.Column(db.Integer)

