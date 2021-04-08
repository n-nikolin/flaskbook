from datetime import datetime
from flaskbook import db, login_manager
from flask_login import UserMixin

# user login
# read more about login_manager and its methods


@login_manager.user_loader
def load_user(user_model_id):
    return UserModel.query.get(int(user_model_id))


class UserModel(db.Model, UserMixin):
    __tablename__ = 'user_model'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    books = db.relationship('Book', backref='user_book', lazy=True)

    # ???? how do i store passwords
    def __init__(self, username, email, password):
        # pass
        self.username = username
        self.email = email
        self.password = password

    def __repr__(self):
        return f"<User('{self.username}', '{self.email}')>"


# TODO (maybe): divide book into author and book schemas
# TODO: add complete(bool) column to take care of date_finished column
class Book(db.Model):
    __tablename__ = 'book'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    author = db.Column(db.String(120), nullable=False)
    #image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    num_pages = db.Column(db.Integer, nullable=False)
    date_started = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)
    date_finished = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)
    complete = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user_model.id'), nullable=False)

    def __repr__(self):
        return f"<BookID: '{self.id}'>"
