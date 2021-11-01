from flask import Flask, render_template, redirect, url_for, abort, flash
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, login_user, LoginManager, fresh_login_required, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from forms import LoginForm, RegisterForm, DispatchForm, TableFilterForm
from util_func import rate_matcher, diesel_matcher
from datetime import datetime, date
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import os

import pandas as pd

# pandas options
pd.options.display.float_format = '{:,.2f}'.format

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(12)
Bootstrap(app)

# Connect to database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lbc_dispatch.db'
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
    dispatch = relationship("Dispatch", back_populates="encoder")


class Dispatch(UserMixin, db.Model):
    __tablename__ = "dispatch"
    id = db.Column(db.Integer, primary_key=True)
    dispatch_date = db.Column(db.String(100), nullable=False)
    slip_no = db.Column(db.String(100), nullable=False)
    route = db.Column(db.String(100), nullable=False)
    area = db.Column(db.String(250))
    odo_start = db.Column(db.Integer)
    odo_end = db.Column(db.Integer)
    km = db.Column(db.Float(precision=2))
    cbm = db.Column(db.String(100), nullable=False)
    qty = db.Column(db.String(100), nullable=False)
    drops = db.Column(db.String(100), nullable=False)
    rate = db.Column(db.String(100), nullable=False)
    plate_no = db.Column(db.String(100), nullable=False)
    driver = db.Column(db.String(100), nullable=False)
    courier = db.Column(db.String(100), nullable=False)
    encoded_on = db.Column(db.String(100), nullable=False)
    encoded_by = db.Column(db.String(100))
    encoder_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    encoder = relationship("User", back_populates="dispatch")
    pay_day = db.Column(db.String(100), nullable=False)
    invoice_no = db.Column(db.String(100))
    or_no = db.Column(db.String(100))
    or_amt = db.Column(db.Float(precision=2))


# Run only once
db.create_all()

# User login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "Strong"  # "basic"


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
    return render_template("index.html")


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
            flash(f"This email: ' {email} ' does not exist. Kindly try again.")
            return redirect(url_for("login"))
        elif not check_password_hash(user.password, password):
            flash("Incorrect password.")
            return redirect(url_for("login"))
        else:
            login_user(user)
            return redirect(url_for("home"))
    return render_template("login.html", form=form)


@app.route("/logout", methods=["Get", "Post"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/dispatch", methods=["Get", "Post"])
# @fresh_login_required
# @admin_only
def input_dispatch():
    form = DispatchForm()
    if form.validate_on_submit():
        # Add new dispatch to database
        new_dispatch = Dispatch(
            dispatch_date=form.dispatch_date.data,
            slip_no=form.slip_no.data,
            route="None".title(),
            area=form.area.data.title(),
            odo_start=form.odo_start.data,
            odo_end=form.odo_end.data,
            km=form.odo_end.data - form.odo_start.data,
            cbm=form.cbm.data,
            qty=form.qty.data,
            drops=form.drops.data,
            rate=form.rate.data,
            plate_no=form.plate_no.data.upper(),
            driver=form.driver.data.title(),
            courier=form.courier.data.title(),
            encoded_on=date.today(),
            encoded_by=current_user.first_name,
            encoder_id=current_user.id,
            invoice_no='-',
            status='-',
            or_no='-'
        )
        db.session.add(new_dispatch)
        db.session.commit()
        return redirect(url_for("dispatch"))
    return render_template("input_dispatch.html", form=form)


@app.route("/dispatch_report", methods=["Get", "Post"])
# @fresh_login_required
# @admin_only
def dispatch():
    # create table filter form
    form = TableFilterForm()

    # Get all dispatch data from database
    with create_engine('sqlite:///lbc_dispatch.db').connect() as cnx:
        df = pd.read_sql_table(table_name="dispatch", con=cnx)

    # Dispatch data
    sorted_df = df.head(n=20).sort_values("dispatch_date", ascending=False)

    # Operation summary
    operation_df = pd.DataFrame(
        sorted_df.groupby(['plate_no', 'dispatch_date', 'driver', 'courier'])['slip_no'].count())
    operation_tb = operation_df.to_html(
        classes='table-striped table-hover table-bordered table-sm',
        justify='match-parent',
    )

    # Operators details
    driver_ser = sorted_df.groupby("driver")["slip_no"].count()
    courier_ser = sorted_df.groupby("courier")["slip_no"].count()
    operators_df = pd.DataFrame(driver_ser.append(courier_ser))
    rate = rate_matcher(operators_df)
    operators_df['Rate'] = rate[0]
    operators_df['Total'] = rate[1]
    operators_tb = operators_df.to_html(
        classes='table-striped table-hover table-bordered table-sm',
        justify='match-parent',
    )

    # Unit details
    unit_df = sorted_df.groupby(['plate_no']).aggregate({'slip_no': 'count', 'km': 'sum'})
    diesel = diesel_matcher(unit_df)
    unit_df['diesel/disp'] = diesel[0]
    unit_df['total diesel'] = diesel[1]
    unit_tb = unit_df.to_html(
        classes='table-striped table-hover table-bordered table-sm',
        justify='match-parent',
    )

    # SORTED DISPATCH DATA
    if form.validate_on_submit():
        # Sort and filter dataframe
        start = form.date_start.data
        end = form.date_end.data
        index = form.filter.data
        filtered_df = df[(df[index] >= str(start)) & (df[index] <= str(end))].sort_values(index, ascending=False)

        # OPEX SUMMARY
        # Dispatch expenses operation summary
        driver_ser = filtered_df.groupby("driver")["slip_no"].count()
        courier_ser = filtered_df.groupby("courier")["slip_no"].count()
        unit_ser = filtered_df.groupby("plate_no")["slip_no"].count()

        combined_ser = driver_ser.append(courier_ser).append(unit_ser)
        summary_df = pd.DataFrame({'Dispatched': combined_ser})

        # Adding rate and total columns to summary dataframe
        matched_list = rate_matcher(combined_ser)
        summary_df['Rate'] = matched_list[0]
        summary_df['Total'] = matched_list[1]
        operators_tb = summary_df.to_html(
            classes='table-striped table-hover table-bordered table-sm',
            justify='match-parent',
        )

        return render_template("dispatch_report.html", form=form, df=filtered_df, opex_tb=operators_tb)
    return render_template("dispatch_report.html", form=form, df=sorted_df, operation_tb=operation_tb, operators_tb=operators_tb, unit_tb=unit_tb)


@app.route("/edit_dispatch/<int:dispatch_id>", methods=["Get", "Post"])
def edit_dispatch(dispatch_id):
    dispatch_to_edit = Dispatch.query.get(dispatch_id)
    # pre-load form
    edit_form = DispatchForm(
        dispatch_date=datetime.strptime(dispatch_to_edit.dispatch_date, "%Y-%m-%d"),
        slip_no=dispatch_to_edit.slip_no,
        route=dispatch_to_edit.route,
        area=dispatch_to_edit.area,
        odo_start=dispatch_to_edit.odo_start,
        odo_end=dispatch_to_edit.odo_end,
        cbm=dispatch_to_edit.cbm,
        qty=dispatch_to_edit.qty,
        drops=dispatch_to_edit.drops,
        rate=dispatch_to_edit.rate,
        plate_no=dispatch_to_edit.plate_no,
        driver=dispatch_to_edit.driver,
        courier=dispatch_to_edit.courier,
    )
    # load back edited form data to db
    if edit_form.validate_on_submit():
        dispatch_to_edit.dispatch_date = edit_form.dispatch_date.data
        dispatch_to_edit.slip_no = edit_form.slip_no.data
        dispatch_to_edit.route = edit_form.route.data.title()
        dispatch_to_edit.area = edit_form.area.data.title()
        dispatch_to_edit.odo_start = edit_form.odo_start.data
        dispatch_to_edit.odo_end = edit_form.odo_end.data
        dispatch_to_edit.km = edit_form.odo_end.data - edit_form.odo_start.data
        dispatch_to_edit.cbm = edit_form.cbm.data
        dispatch_to_edit.qty = edit_form.qty.data
        dispatch_to_edit.drops = edit_form.drops.data
        dispatch_to_edit.rate = edit_form.rate.data
        dispatch_to_edit.plate_no = edit_form.plate_no.data.upper()
        dispatch_to_edit.driver = edit_form.driver.data.title()
        dispatch_to_edit.courier = edit_form.courier.data.title()
        dispatch_to_edit.encoded_on = str(date.today())
        dispatch_to_edit.encoded_by = current_user.first_name
        db.session.commit()
        return redirect(url_for("dispatch"))
    return render_template("input_dispatch.html", form=edit_form)


@app.route("/delete_dispatch/<int:dispatch_id>", methods=["Get", "Post"])
def delete_dispatch(dispatch_id):
    dispatch_to_delete = Dispatch.query.get(dispatch_id)
    db.session.delete(dispatch_to_delete)
    db.session.commit()
    return redirect(url_for("dispatch"))


if __name__ == "__main__":
    app.run(debug=True)
