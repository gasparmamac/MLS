from flask import Flask, render_template, redirect, url_for, abort, flash
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from forms import LoginForm, RegisterForm, DispatchForm
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(12)
Bootstrap(app)

# Connect to database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mls_operation.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Database tables
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    first_name = db.Column(db.String(100))
    middle_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))


# Run only once
db.create_all()

# User login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function


# My apps ----------------------------------------------
@app.route("/", methods=["Get", "Post"])
def home():
    users = User.query.all()
    return render_template("index.html", users=users)


@app.route("/register", methods=["Get", "Post"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        # Confirm if the registrant is not on the database
        if User.query.filter_by(email=form.email.data).first():
            print('Hello')
            flash(f"This email: {form.email.data} is already registered.")
            return redirect(url_for("register"))

        # hash and salt password
        hashed_and_salted_password = generate_password_hash(
            form.password.data,
            method="pbkdf2:sha256",
            salt_length=8
        )
        # Add new user to the database
        new_user = User(
            email=form.email.data,
            first_name=form.first_name.data,
            middle_name=form.middle_name.data,
            last_name=form.last_name.data,
            password=hashed_and_salted_password
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("home"))
    return render_template("register.html", form=form)


@app.route("/login", methods=["Get", "Post"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # get login data
        email = form.email.data
        password = form.password.data

        # check login data
        user = User.query.filter_by(email=email).first()
        if not user:
            flash(f"This email: {email} does not exist. Kindly try again.")
            return redirect(url_for("login"))
        elif not check_password_hash(user.password, password):
            print(user.password)
            flash("Incorrect password.")
            return redirect(url_for("login"))
        else:
            login_user(user)
            return redirect(url_for("home"))
    return render_template("login.html", form=form)


@app.route("/login", methods=["Get", "Post"])
# @login_required
def logout():
    load_user()
    return redirect(url_for("home"))


@app.route("/dispatch", methods=["Get", "Post"])
def dispatch():
    form = DispatchForm()
    return render_template("dispatch.html", form=form)


if __name__ == "__main__":
    app.run(debug=True)
