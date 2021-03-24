import os
from datetime import timedelta
from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mtg-stone.sqlite'
app.secret_key = os.environ.get("SECRET_KEY")
app.permanent_session_lifetime = timedelta(minutes=5)
CORS(app, supports_credentials=True)
db = SQLAlchemy(app)
ma = Marshmallow(app)
flask_bcrypt = Bcrypt(app)

cards = db.Table('cards',
                 db.Column('card_id', db.Integer, db.ForeignKey(
                     'card.id'), primary_key=True),
                 db.Column('user_id', db.Integer, db.ForeignKey(
                     'user.id'), primary_key=True)
                 )


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    cards = db.relationship('Card', secondary=cards, lazy='subquery',
                            backref=db.backref('users', lazy=True))


class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(141), unique=True, nullable=False)


class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "username", "email", "password")


user_schema = UserSchema()
users_schema = UserSchema(many=True)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route("/mtg-stone/sign-up", methods=["POST"])
def register():
    post_data = request.get_json()
    username = post_data.get("username")
    email = post_data.get("email")
    password = post_data.get("password")
    db_user = User.query.filter_by(username=username).first()
    if db_user:
        return "Username taken", 409
    hashed_password = flask_bcrypt.generate_password_hash(
        password).decode("utf-8")
    new_user = User(username=username, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    session.permanent = True
    session["username"] = username
    print(session)
    return jsonify(user_schema.dump(new_user))


@app.route("/mtg-stone/log-in", methods=["POST"])
def login():
    post_data = request.get_json()
    db_user = User.query.filter_by(username=post_data.get("username")).first()
    if db_user is None:
        return "Username NOT found", 404
    password = post_data.get("password")
    db_user_hashed_password = db_user.password
    valid_password = flask_bcrypt.check_password_hash(
        db_user_hashed_password, password)
    if valid_password:
        session.permanent = True
        session["username"] = post_data.get("username")
        return jsonify("User Verified")
    return "password invalid", 401


@app.route("/mtg-stone/user/<id>", methods=["DELETE"])
def delete_user(id):
    user = User.query.filter_by(id=id).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return "User deleted"
    return "user not found", 404


@app.route("/mtg-stone/user/<id>", methods=["GET"])
def user(id):
    user = User.query.get(id)
    return jsonify(user_schema.dump(user))


@app.route("/mtg-stone/users")
def get_users():
    all_users = User.query.all()
    return jsonify(users_schema.dump(all_users))


if __name__ == "__main__":
    app.run(debug=True)
