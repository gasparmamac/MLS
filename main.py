from flask import Flask, render_template, redirect, url_for, abort, flash, request
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, login_user, LoginManager, fresh_login_required, login_required, \
    current_user, logout_user
from flask_wtf import CSRFProtect
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
# email
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

import pdfkit
from num2words import num2words
from _forms import *
from _util import *

from datetime import datetime, date
from sqlalchemy import create_engine
import os

import pandas as pd

# pandas options
pd.options.display.float_format = '{:,.1f}'.format

app = Flask(__name__)
# SECRET_KEY = os.urandom(16)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
# app.config['SECRET_KEY'] = SECRET_KEY
Bootstrap(app)

# Connect to database

# heroku posgres-alchemy issue sol'n'( 'SQLAlchemy 1.4.x has removed support for the postgres:// URI scheme')
uri = os.environ.get('DATABASE_URL', 'sqlite:///lbc2_dispatch.db')
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
csrf = CSRFProtect(app)
csrf.init_app(app)


# Tables------------------------------------------------------------------

class UserTable(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    email = db.Column(db.String(250), unique=True)
    password = db.Column(db.String(250))
    first_name = db.Column(db.String(250))
    middle_name = db.Column(db.String(250))
    last_name = db.Column(db.String(250))
    extn_name = db.Column(db.String(250))
    full_name = db.Column(db.String(250))
    admin = db.Column(db.String(250))
    dispatch = relationship("DispatchTable", back_populates="encoder")
    admin_exp = relationship("AdminExpenseTable", back_populates="encoder")
    maintenance = relationship("MaintenanceTable", back_populates="encoder")


class DispatchTable(UserMixin, db.Model):
    __tablename__ = "dispatch"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    dispatch_date = db.Column(db.String(250), nullable=False)
    wd_code = db.Column(db.String(250), nullable=False)
    slip_no = db.Column(db.String(250), nullable=False)
    route = db.Column(db.String(250), nullable=False)
    area = db.Column(db.String(250))
    destination = db.Column(db.String(250))
    odo_start = db.Column(db.Integer)
    odo_end = db.Column(db.Integer)
    km = db.Column(db.Float(precision=1))
    cbm = db.Column(db.Float(precision=1), nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    drops = db.Column(db.Integer, nullable=False)
    std_rate = db.Column(db.Float(precision=1), nullable=False)
    rate = db.Column(db.Float(precision=1), nullable=False)
    plate_no = db.Column(db.String(250), nullable=False)
    driver = db.Column(db.String(250), nullable=False)
    courier = db.Column(db.String(250), nullable=False)
    forwarded_date = db.Column(db.String(250), nullable=False)
    invoice_no = db.Column(db.String(250))
    or_no = db.Column(db.String(250))
    or_amt = db.Column(db.Float(precision=1))
    encoded_on = db.Column(db.String(250), nullable=False)
    encoded_by = db.Column(db.String(250))
    encoder_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    encoder = relationship("UserTable", back_populates="dispatch")
    date_settled = db.Column(db.String(250))


class MaintenanceTable(UserMixin, db.Model):
    __tablename__ = "maintenance"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    date = db.Column(db.String(250), nullable=False)
    plate_no = db.Column(db.String(250), nullable=False)
    type = db.Column(db.String(250), nullable=False)
    comment = db.Column(db.String(250), nullable=False)
    pyesa_amt = db.Column(db.Float(precision=1))
    tools_amt = db.Column(db.Float(precision=1))
    service_charge = db.Column(db.Float(precision=1))
    total_amt = db.Column(db.Float(precision=1))
    encoded_by = db.Column(db.String(250))
    encoder_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    encoder = relationship("UserTable", back_populates="maintenance")
    date_settled = db.Column(db.String(250))


class AdminExpenseTable(UserMixin, db.Model):
    __tablename__ = "admin"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    date = db.Column(db.String(250), nullable=False)
    agency = db.Column(db.String(250), nullable=False)
    office = db.Column(db.String(250), nullable=False)
    frequency = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    amount = db.Column(db.Float(precision=1))
    encoded_by = db.Column(db.String(250))
    encoder_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    encoder = relationship("UserTable", back_populates="admin_exp")
    date_settled = db.Column(db.String(250))


class PayStripTable(UserMixin, db.Model):
    __tablename__ = "pay_strip"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    date_settled = db.Column(db.String(250))
    start_date = db.Column(db.String(250), nullable=False)
    end_date = db.Column(db.String(250), nullable=False)
    employee_name = db.Column(db.String(250), nullable=False)
    employee_id = db.Column(db.String(250), nullable=False)

    # attendance
    normal = db.Column(db.Integer)
    reg_hol = db.Column(db.Integer)
    no_sp_hol = db.Column(db.Integer)
    wk_sp_hol = db.Column(db.Integer)
    rd = db.Column(db.Integer)
    equiv_wd = db.Column(db.Float(precision=2))

    # pay
    basic = db.Column(db.Float(precision=2))
    allowance1 = db.Column(db.Float(precision=2))
    allowance2 = db.Column(db.Float(precision=2))
    allowance3 = db.Column(db.Float(precision=2))
    pay_adj = db.Column(db.Float(precision=2))
    pay_adj_reason = db.Column(db.String(250))

    # deduction
    cash_adv = db.Column(db.Float(precision=2))
    ca_date = db.Column(db.String(250))
    ca_deduction = db.Column(db.Float(precision=2))
    ca_remaining = db.Column(db.Float(precision=2))
    sss = db.Column(db.Float(precision=2))
    philhealth = db.Column(db.Float(precision=2))
    pag_ibig = db.Column(db.Float(precision=2))
    life_insurance = db.Column(db.Float(precision=2))
    income_tax = db.Column(db.Float(precision=2))

    # summary
    total_pay = db.Column(db.Float(precision=2))
    total_deduct = db.Column(db.Float(precision=2))
    net_pay = db.Column(db.Float(precision=2))
    transferred_amt1 = db.Column(db.Float(precision=2))
    transferred_amt2 = db.Column(db.Float(precision=2))
    carry_over_next_month = db.Column(db.Float(precision=2))
    carry_over_past_month = db.Column(db.Float(precision=2))

    gen_date = db.Column(db.String(250))
    paid_by = db.Column(db.String(250))
    dispatch_ids = db.Column(db.String(250))


class EmployeeProfileTable(UserMixin, db.Model):
    __tablename__ = "employee"
    id = db.Column(db.Integer, primary_key=True, unique=True)

    # personal info
    first_name = db.Column(db.String(250), nullable=False)
    middle_name = db.Column(db.String(250), nullable=False)
    last_name = db.Column(db.String(250), nullable=False)
    extn_name = db.Column(db.String(250), nullable=False)
    full_name = db.Column(db.String(250), nullable=False)
    birthday = db.Column(db.String(250), nullable=False)
    gender = db.Column(db.String(250), nullable=False)
    contact_no = db.Column(db.String(250), nullable=False)
    facebook = db.Column(db.String(250))


    # address
    address = db.Column(db.String(250))

    # CompanyInfo
    employee_id = db.Column(db.String(250))
    date_hired = db.Column(db.String(250))
    date_resigned = db.Column(db.String(250))
    employment_status = db.Column(db.String(250))
    position = db.Column(db.String(250))
    rank = db.Column(db.String(250))

    # Benefits
    sss_no = db.Column(db.String(250))
    philhealth_no = db.Column(db.String(250))
    pag_ibig_no = db.Column(db.String(250))
    # benefits premiums
    sss_prem = db.Column(db.Float(precision=2))
    philhealth_prem = db.Column(db.Float(precision=2))
    pag_ibig_prem = db.Column(db.Float(precision=2))
    # deductions
    cash_adv = db.Column(db.Float(precision=2))
    ca_date = db.Column(db.String(250))
    ca_deduction = db.Column(db.Float(precision=2))
    ca_remaining = db.Column(db.Float(precision=2))

    # Compensation
    basic = db.Column(db.Float(precision=2))
    allowance1 = db.Column(db.Float(precision=2))
    allowance2 = db.Column(db.Float(precision=2))
    allowance3 = db.Column(db.Float(precision=2))

    encoded_on = db.Column(db.String(250))
    encoded_by = db.Column(db.String(250))


class Tariff(db.Model, UserMixin):
    __tablename__ = 'tariff'
    id = db.Column(db.Integer, primary_key=True, unique=True)
    route = db.Column(db.String(250), nullable=True)
    area = db.Column(db.String(250), nullable=True)
    km = db.Column(db.Float(precision=1))
    vehicle = db.Column(db.String(250))
    cbm = db.Column(db.Float(precision=1))
    rate = db.Column(db.Float(precision=1))
    diesel = db.Column(db.Float(precision=1))
    update = db.Column(db.String(250))
    encoded_on = db.Column(db.String(250))
    encoded_by = db.Column(db.String(250))


class Invoice(db.Model, UserMixin):
    __tablename__ = 'invoice'
    id = db.Column(db.Integer, primary_key=True, unique=True)
    invoice_series = db.Column(db.Integer)
    invoice_no = db.Column(db.String(250), unique=True)
    slip_nos = db.Column(db.String(250))
    plate_no = db.Column(db.String(250))
    dispatch_cnt = db.Column(db.Integer)
    gross_pay = db.Column(db.Float(precision=1))
    less = db.Column(db.Float(precision=1))
    amount_due = db.Column(db.Float(precision=1))
    paid = db.Column(db.String(250))
    or_no = db.Column(db.String(250))
    issued_on = db.Column(db.String(250))
    prepared_date = db.Column(db.String(250))
    prepared_by = db.Column(db.String(250))

    # not displayed
    dispatch_ids = db.Column(db.String(250))


class Trasaction(db.Model, UserMixin):
    __tablename__ = "transaction"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    trans_date = db.Column(db.String(250))
    paystrip_ids = db.Column(db.String(250))
    maintenance_ids = db.Column(db.String(250))
    admin_ids = db.Column(db.String(250))
    by = db.Column(db.String(250))
    on = db.Column(db.String(250))


# Run only once
db.create_all()


# ------------------------------------------Login-logout setup and config---------------------------------------------
# User login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "Basic"  # "Strong"


@login_manager.user_loader
def load_user(user_id):
    return UserTable.query.get(int(user_id))


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id >= 3:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function


# Login-logout-------------------------------------------------------
@app.route("/", methods=["Get", "Post"])
def home():

    # step0: get fresh copy of dispatch
    # step1: check if there's unpaid dispatch
    # step2: group unpaid dispatch
    # step3: regroup step2 per vehicle
    # step4: display table

    # First check user
    with create_engine(uri).connect() as cnx1:
        _user = pd.read_sql_table(table_name="users", con=cnx1)
    no_user = _user.dropna().empty

    if no_user:
        return redirect(url_for('register'))
    elif not current_user.is_authenticated:
        return redirect(url_for('login'))

# Dispatch
    with create_engine(uri).connect() as cnx:
        disp_df = pd.read_sql_table(table_name="dispatch", con=cnx, columns=[
            'id', 'dispatch_date', 'plate_no', 'wd_code', 'slip_no', 'destination', 'driver', 'courier', 'forwarded_date'])

    # step1
    unpaid_cnt = is_found(disp_df["forwarded_date"], "-")
    if unpaid_cnt > 0:
        # step2
        disp_grp = disp_df.groupby("forwarded_date").get_group("-")
    else:
        disp_grp = "none"


# Invoice
    # step0
    with create_engine(uri).connect() as cnx:
        inv_df = pd.read_sql_table(table_name="invoice", con=cnx, columns=[
            'id', 'invoice_no', 'plate_no', 'dispatch_cnt', 'slip_nos', 'or_no'])

    # step1
    unpaid_inv_cnt = is_found(inv_df['or_no'], "-")
    if unpaid_inv_cnt > 0:
        inv_grp = inv_df.groupby("or_no").get_group("-")
    else:
        inv_grp = "none"

    return render_template("_index.html", disp_grp=disp_grp, inv_grp=inv_grp, unpaid_inv_cnt=unpaid_inv_cnt, unpaid_cnt=unpaid_cnt)


@app.route("/register", methods=["Get", "Post"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        # Confirm if the registrant is not on the database
        if UserTable.query.filter_by(email=form.email.data).first():
            flash(f"This email: {form.email.data} is already registered.")
            return redirect(url_for("register"))

        # hash and salt password
        hashed_and_salted_password = generate_password_hash(
            form.password.data,
            method="pbkdf2:sha256",
            salt_length=8
        )

        # full name construction
        if form.extn_name.data == "":
            full_name = f"{form.first_name.data.title()} {form.middle_name.data[0].title()}. {form.last_name.data.title()}"
        else:
            full_name = f"{form.first_name.data.title()} {form.middle_name.data[0].title()}. {form.last_name.data.title()} {form.extn_name.data.title()}"

        # Add new user to the database
        new_user = UserTable(
            email=form.email.data.lower(),
            first_name=form.first_name.data.title(),
            middle_name=form.middle_name.data.title(),
            last_name=form.last_name.data.title(),
            extn_name=form.extn_name.data.title(),
            full_name=full_name,
            password=hashed_and_salted_password,
            admin='False'
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("home"))
    return render_template("_register.html", form=form)


@app.route("/login", methods=["Get", "Post"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # get login data
        email = form.email.data
        password = form.password.data

        # check login data
        user = UserTable.query.filter_by(email=email).first()
        if not user:
            flash(f"This email: ' {email} ' does not exist. Kindly try again.")
            return redirect(url_for("login"))
        elif not check_password_hash(user.password, password):
            flash("Incorrect password.")
            return redirect(url_for("login"))
        else:
            login_user(user)
            return redirect(url_for("home"))
    return render_template("_login.html", form=form)


@app.route("/logout", methods=["Get", "Post"])
def logout():
    logout_user()
    return redirect(url_for("home"))


# Dispatch table--------------------------------------------------------
@app.route("/dispatch_report", methods=["Get", "Post"])
# @admin_only
@login_required
def dispatch():
    # check employee and tariff
    with create_engine(uri).connect() as cnx2:
        _tariff = pd.read_sql_table(table_name="tariff", con=cnx2)
    with create_engine(uri).connect() as cnx3:
        _emp = pd.read_sql_table(table_name="employee", con=cnx3)

    no_tariff = _tariff.dropna().empty
    no_emp = _emp.dropna().empty

    if no_emp:
        return redirect(url_for('employee_add'))
    elif no_tariff:
        return redirect((url_for('add_tariff')))

    # create table filter form
    form = DispatchTableFilterForm()

    # Get all dispatch data from database
    with create_engine(uri).connect() as cnx:
        df = pd.read_sql_table(table_name="dispatch", con=cnx)

    # Dispatch data
    sorted_df = df.head(n=25).sort_values("dispatch_date", ascending=False)

    # SORTED DISPATCH DATA
    if form.validate_on_submit():
        # Sort and filter dataframe
        start = form.date_start.data
        end = form.date_end.data
        index = form.filter.data
        filtered_df = df[(df[index] >= str(start)) & (df[index] <= str(end))].sort_values(index, ascending=False)
        return render_template("dispatch_data.html", form=form, df=filtered_df)
    return render_template("dispatch_data.html", form=form, df=sorted_df, no_emp=no_emp, no_tariff=no_tariff)


@app.route("/input_dispatch", methods=["Get", "Post"])
@admin_only
@login_required
def input_dispatch():
    form = DispatchForm()
    form.driver.choices = [g.full_name for g in EmployeeProfileTable.query.order_by("last_name")]
    form.courier.choices = [g.full_name for g in EmployeeProfileTable.query.order_by("last_name")]
    form.area.choices = [a.area for a in Tariff.query.order_by("area")]

    if form.validate_on_submit():
        # get tariff rate
        area = Tariff.query.filter_by(area=form.area.data).first()
        std_rate = area.rate

        # Add new dispatch to database
        new_dispatch = DispatchTable(
            dispatch_date=form.dispatch_date.data.strftime("%Y-%m-%d-%a"),
            wd_code=form.wd_code.data,
            slip_no=form.slip_no.data,
            route="-",
            area=form.area.data.title(),
            destination=form.destination.data.title(),
            odo_start=form.odo_start.data,
            odo_end=form.odo_end.data,
            km=form.odo_end.data - form.odo_start.data,
            cbm=form.cbm.data,
            qty=form.qty.data,
            drops=form.drops.data,
            rate=form.rate.data,
            std_rate=std_rate,
            plate_no=form.plate_no.data.upper(),
            driver=form.driver.data.title(),
            courier=form.courier.data.title(),
            encoded_on=date.today().strftime("%Y-%m-%d-%a"),
            encoded_by=current_user.full_name,
            encoder_id=1,
            forwarded_date='-',
            invoice_no='-',
            or_no='-',
            or_amt=0,
            date_settled='-'
        )
        db.session.add(new_dispatch)
        db.session.commit()
        return redirect(url_for("dispatch"))
    return render_template("dispatch_input.html", form=form)


@app.route("/edit_dispatch/<int:dispatch_id>", methods=["Get", "Post"])
@admin_only
@login_required
def edit_dispatch(dispatch_id):
    dispatch_to_edit = DispatchTable.query.get(dispatch_id)
    # pre-load form
    edit_form = DispatchForm(
        dispatch_date=datetime.strptime(dispatch_to_edit.dispatch_date, "%Y-%m-%d-%a"),
        wd_code=dispatch_to_edit.wd_code,
        slip_no=dispatch_to_edit.slip_no,
        route=dispatch_to_edit.route,
        area=dispatch_to_edit.area,
        destination=dispatch_to_edit.destination,
        odo_start=dispatch_to_edit.odo_start,
        odo_end=dispatch_to_edit.odo_end,
        cbm=dispatch_to_edit.cbm,
        qty=dispatch_to_edit.qty,
        drops=dispatch_to_edit.drops,
        rate=dispatch_to_edit.rate,
        plate_no=dispatch_to_edit.plate_no,
    )
    # choices for select field
    choices1 = ["-"]
    choices2 = ["-"]

    a = [g.full_name for g in EmployeeProfileTable.query.order_by("last_name")]
    b = [a.area for a in Tariff.query.order_by("area")]

    choices1 += a
    choices2 += b

    edit_form.driver.choices = choices1
    edit_form.courier.choices = choices1
    edit_form.area.choices = choices2

    # load back edited form data to db
    if edit_form.validate_on_submit():
        # get area details
        area = Tariff.query.filter_by(area=edit_form.area.data).first()

        dispatch_to_edit.dispatch_date = edit_form.dispatch_date.data.strftime("%Y-%m-%d-%a")
        dispatch_to_edit.wd_code = edit_form.wd_code.data
        dispatch_to_edit.slip_no = edit_form.slip_no.data
        dispatch_to_edit.route = area.route
        dispatch_to_edit.area = edit_form.area.data.title()
        dispatch_to_edit.destination = edit_form.destination.data.title()
        dispatch_to_edit.odo_start = edit_form.odo_start.data
        dispatch_to_edit.odo_end = edit_form.odo_end.data
        dispatch_to_edit.km = edit_form.odo_end.data - edit_form.odo_start.data
        dispatch_to_edit.cbm = edit_form.cbm.data
        dispatch_to_edit.qty = edit_form.qty.data
        dispatch_to_edit.drops = edit_form.drops.data
        dispatch_to_edit.rate = edit_form.rate.data
        dispatch_to_edit.std_rate = area.rate
        dispatch_to_edit.plate_no = edit_form.plate_no.data.upper()
        dispatch_to_edit.driver = edit_form.driver.data.title()
        dispatch_to_edit.courier = edit_form.courier.data.title()
        dispatch_to_edit.encoded_on = str(date.today().strftime("%Y-%m-%d-%a"))
        dispatch_to_edit.encoded_by = current_user.full_name
        db.session.commit()
        return redirect(url_for("dispatch"))
    return render_template("dispatch_input.html", form=edit_form)


@app.route("/delete_dispatch/<int:dispatch_id>", methods=["Get", "Post"])
@admin_only
@login_required
def delete_dispatch(dispatch_id):
    dispatch_to_delete = DispatchTable.query.get(dispatch_id)
    db.session.delete(dispatch_to_delete)
    db.session.commit()
    return redirect(url_for("dispatch"))


# Maintenance expenses table---------------------------------------------
@app.route("/maintenance", methods=["Get", "Post"])
@admin_only
@login_required
def maintenance():
    form = MaintenanceFilterForm()
    # Get all maintenance data from database
    with create_engine(uri).connect() as cnx:
        df = pd.read_sql_table(table_name="maintenance", con=cnx)

    sorted_df = df.head(n=10).sort_values("date", ascending=False)
    if form.validate_on_submit():
        # Sort and filter dataframe
        start = form.date_start.data
        end = form.date_end.data
        index = "date"
        filtered_df = df[(df[index] >= str(start)) & (df[index] <= str(end))].sort_values(index, ascending=False)
        return render_template("maintenance_data.html", form=form, df=filtered_df)

    return render_template("maintenance_data.html", form=form, df=sorted_df)


@app.route("/input_maintenance", methods=["Get", "Post"])
@admin_only
@login_required
def input_maintenance():
    form = MaintenanceForm()
    if form.validate_on_submit():
        # load form data to database
        new_record = MaintenanceTable(
            date=form.date.data.strftime("%Y-%m-%d-%a"),
            plate_no=form.plate_no.data.upper(),
            type=form.type.data.title(),
            comment=form.comment.data.title(),
            pyesa_amt=form.pyesa_amt.data,
            tools_amt=form.tools_amt.data,
            service_charge=form.service_charge.data,
            total_amt=form.pyesa_amt.data + form.tools_amt.data + form.service_charge.data,
            encoded_by=current_user.full_name.title(),
            date_settled='-',
            encoder_id=current_user.id
        )
        db.session.add(new_record)
        db.session.commit()
        return redirect(url_for('maintenance'))
    return render_template("maintenance_input.html", form=form)


@app.route("/edit_maintenance/<int:maintenance_id>", methods=["Get", "Post"])
@admin_only
@login_required
def edit_maintenance(maintenance_id):
    maintenance_to_edit = MaintenanceTable.query.get(maintenance_id)
    # pre-load form
    edit_form = MaintenanceForm(
        date=datetime.strptime(maintenance_to_edit.date, "%Y-%m-%d-%a"),
        plate_no=maintenance_to_edit.plate_no,
        type=maintenance_to_edit.type,
        comment=maintenance_to_edit.comment,
        pyesa_amt=maintenance_to_edit.pyesa_amt,
        tools_amt=maintenance_to_edit.tools_amt,
        service_charge=maintenance_to_edit.service_charge,
    )
    # load back edited form-data to database
    if edit_form.validate_on_submit():
        maintenance_to_edit.date = edit_form.date.data.strftime("%Y-%m-%d-%a")
        maintenance_to_edit.plate_no = edit_form.plate_no.data.upper()
        maintenance_to_edit.type = edit_form.type.data.title()
        maintenance_to_edit.comment = edit_form.comment.data.title()
        maintenance_to_edit.pyesa_amt = edit_form.pyesa_amt.data
        maintenance_to_edit.tools_amt = edit_form.tools_amt.data
        maintenance_to_edit.service_charge = edit_form.service_charge.data
        maintenance_to_edit.encoded_by = current_user.full_name.title()
        maintenance_to_edit.encoder_id = current_user.id
        db.session.commit()
        return redirect(url_for('maintenance'))
    return render_template("maintenance_input.html", form=edit_form)


@app.route("/delete_maintenance/<int:maintenance_id>", methods=["Get", "Post"])
@admin_only
@login_required
def delete_maintenance(maintenance_id):
    maintenance_to_delete = MaintenanceTable.query.get(maintenance_id)
    db.session.delete(maintenance_to_delete)
    db.session.commit()
    return redirect(url_for('maintenance'))


# Admin expenses--------------------------------------------------------
@app.route("/admin", methods=["Get", "Post"])
@admin_only
@login_required
def admin():
    form = AdminFilterForm()
    # Get all admin expenses data from database
    with create_engine(uri).connect() as cnx:
        df = pd.read_sql_table(table_name="admin", con=cnx)

    sorted_df = df.head(n=10).sort_values("date", ascending=False)
    if form.validate_on_submit():
        # Sort and filter dataframe
        start = form.date_start.data
        end = form.date_end.data
        index = "date"
        filtered_df = df[(df[index] >= str(start)) & (df[index] <= str(end))].sort_values(index, ascending=False)
        return render_template("admin_data.html", form=form, df=filtered_df)
    return render_template("admin_data.html", form=form, df=sorted_df)


@app.route("/input_admin", methods=["Get", "Post"])
@admin_only
@login_required
def input_admin():
    form = AdminExpenseForm()
    if form.validate_on_submit():
        # load form data to database
        new_record = AdminExpenseTable(
            date=form.date.data.strftime("%Y-%m-%d-%a"),
            agency=form.agency.data.upper(),
            office=form.office.data.title(),
            frequency=form.frequency.data.title(),
            description=form.description.data.title(),
            amount=form.amount.data,
            encoded_by=current_user.full_name.title(),
            date_settled='-',
            encoder_id=current_user.id
        )
        db.session.add(new_record)
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template("admin_input.html", form=form)


@app.route("/edit_admin/<int:admin_id>", methods=["Get", "Post"])
@admin_only
@login_required
def edit_admin(admin_id):
    admin_to_edit = AdminExpenseTable.query.get(admin_id)
    # pre-load form
    edit_form = AdminExpenseForm(
        date=datetime.strptime(admin_to_edit.date, "%Y-%m-%d-%a"),
        agency=admin_to_edit.agency,
        office=admin_to_edit.office,
        frequency=admin_to_edit.frequency,
        description=admin_to_edit.description,
        amount=admin_to_edit.amount
    )
    # load back edited form-data to database
    if edit_form.validate_on_submit():
        admin_to_edit.date = edit_form.date.data.strftime("%Y-%m-%d-%a")
        admin_to_edit.agency = edit_form.agency.data.upper()
        admin_to_edit.office = edit_form.office.data.title()
        admin_to_edit.frequency = edit_form.frequency.data.title()
        admin_to_edit.description = edit_form.description.data.title()
        admin_to_edit.amount = edit_form.amount.data
        admin_to_edit.encoded_by = current_user.full_name.title()
        admin_to_edit.encoder_id = current_user.id
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template("admin_input.html", form=edit_form)


@app.route("/delete_admin/<int:admin_id>", methods=["Get", "Post"])
@admin_only
@login_required
def delete_admin(admin_id):
    admin_to_delete = AdminExpenseTable.query.get(admin_id)
    db.session.delete(admin_to_delete)
    db.session.commit()
    return redirect(url_for('admin'))


# Employee-------------------------------------------------------------
@app.route("/employee_list", methods=["Get", "Post"])
@admin_only
@login_required
def employees():
    # Get all employees data from database
    with create_engine(uri).connect() as cnx:
        df = pd.read_sql_table(table_name="employee", con=cnx)
    return render_template("employees_data.html", df=df)


@app.route("/employee_add", methods=["Get", "Post"])
@admin_only
@login_required
def employee_add():
    form = EmployeeEntryForm()
    if form.validate_on_submit():

        # full name construction
        if form.extn_name.data == "":
            full_name = f"{form.first_name.data.title()} {form.middle_name.data[0].title()}. {form.last_name.data.title()}"
        else:
            full_name = f"{form.first_name.data.title()} {form.middle_name.data[0].title()}. {form.last_name.data.title()} {form.extn_name.data.title()}"

        new_employee = EmployeeProfileTable(
            # personal info
            first_name=form.first_name.data.title(),
            middle_name=form.middle_name.data.title(),
            last_name=form.last_name.data.title(),
            extn_name=form.extn_name.data.title(),
            full_name=full_name,
            birthday=form.birthday.data.strftime("%Y-%m-%d-%a"),
            gender=form.gender.data.title(),
            # address
            address=form.address.data.title(),
            contact_no=form.contact_no.data,
            facebook=form.facebook.data,
            # CompanyInfo
            employee_id="-",
            date_hired=date.today().strftime("%Y-%m-%d-%a"),
            date_resigned="-",
            employment_status="-",
            position="-",
            rank="-",
            # Benefits
            sss_no="-",
            philhealth_no="-",
            pag_ibig_no="-",
            # benefits premiums
            sss_prem=0,
            philhealth_prem=0,
            pag_ibig_prem=0,
            # deductions
            cash_adv=0,
            ca_date="-",
            ca_deduction=0,
            ca_remaining=0,
            # Compensation
            basic=0,
            allowance1=0,
            allowance2=0,
            allowance3=0,

            # others
            encoded_on=datetime.today().strftime("%Y-%m-%d"),
            encoded_by=current_user.full_name
        )
        db.session.add(new_employee)
        db.session.commit()
        return redirect(url_for("employees"))
    return render_template("employees_input.html", form=form)


@app.route("/employee_edit/<int:employee_index>", methods=["Get", "Post"])
@admin_only
@login_required
def employee_edit(employee_index):
    employee_to_edit = EmployeeProfileTable.query.get(employee_index)
    # pre-load form
    edit_form = EmployeeEntryForm(
        first_name=employee_to_edit.first_name,
        middle_name=employee_to_edit.middle_name,
        last_name=employee_to_edit.last_name,
        extn_name=employee_to_edit.extn_name,
        birthday=datetime.strptime(employee_to_edit.birthday, "%Y-%m-%d-%a"),
        gender=employee_to_edit.gender,
        address=employee_to_edit.address,
        contact_no=employee_to_edit.contact_no,
        facebook=employee_to_edit.facebook

    )
    # reload edited form to db
    if edit_form.validate_on_submit():

        # full name construction
        if edit_form.extn_name.data == "":
            full_name = f"{edit_form.first_name.data.title()} {edit_form.middle_name.data[0].title()}. {edit_form.last_name.data.title()}"
        else:
            full_name = f"{edit_form.first_name.data.title()} {edit_form.middle_name.data[0].title()}. {edit_form.last_name.data.title()} {edit_form.extn_name.data.title()}"

        employee_to_edit.first_name = edit_form.first_name.data.title()
        employee_to_edit.middle_name = edit_form.middle_name.data.title()
        employee_to_edit.last_name = edit_form.last_name.data.title()
        employee_to_edit.extn_name = edit_form.extn_name.data.title()
        employee_to_edit.full_name = full_name
        employee_to_edit.birthday = edit_form.birthday.data.strftime("%Y-%m-%d-%a")
        employee_to_edit.gender = edit_form.gender.data.title()
        employee_to_edit.address = edit_form.address.data.title()
        employee_to_edit.contact_no = edit_form.contact_no.data
        employee_to_edit.facebook = edit_form.facebook.data
        db.session.commit()
        return redirect(url_for("employees"))
    return render_template("employees_input.html", form=edit_form)


@app.route("/employee_admin_edit/<int:employee_index>", methods=["Get", "Post"])
@admin_only
@login_required
def employee_admin_edit(employee_index):
    employee_to_edit = EmployeeProfileTable.query.get(employee_index)
    # pre-load form
    edit_form = EmployeeAdminEditForm(
        employee_id=employee_to_edit.employee_id,
        date_hired=datetime.strptime(employee_to_edit.date_hired, "%Y-%m-%d-%a"),
        employment_status=employee_to_edit.employment_status,
        position=employee_to_edit.position,
        rank=employee_to_edit.rank,
        sss_no=employee_to_edit.sss_no,
        philhealth_no=employee_to_edit.philhealth_no,
        pag_ibig_no=employee_to_edit.pag_ibig_no,
        sss_prem=employee_to_edit.sss_prem,
        philhealth_prem=employee_to_edit.philhealth_prem,
        pag_ibig_prem=employee_to_edit.pag_ibig_prem,
        basic=employee_to_edit.basic,
        allowance1=employee_to_edit.allowance1,
        allowance2=employee_to_edit.allowance2,
        allowance3=employee_to_edit.allowance3
    )
    if edit_form.validate_on_submit():
        employee_to_edit.employee_id = edit_form.employee_id.data.upper()
        employee_to_edit.date_hired = edit_form.date_hired.data.strftime("%Y-%m-%d-%a")
        employee_to_edit.employment_status = edit_form.employment_status.data.upper()
        employee_to_edit.position = edit_form.position.data.upper()
        employee_to_edit.rank = edit_form.rank.data.upper()
        employee_to_edit.sss_no = edit_form.sss_no.data.upper()
        employee_to_edit.philhealth_no = edit_form.philhealth_no.data.upper()
        employee_to_edit.pag_ibig_no = edit_form.pag_ibig_no.data.upper()
        employee_to_edit.sss_prem = edit_form.sss_prem.data
        employee_to_edit.philhealth_prem = edit_form.philhealth_prem.data
        employee_to_edit.pag_ibig_prem = edit_form.pag_ibig_prem.data
        employee_to_edit.basic = edit_form.basic.data
        employee_to_edit.allowance1 = edit_form.allowance1.data
        employee_to_edit.allowance2 = edit_form.allowance2.data
        employee_to_edit.allowance3 = edit_form.allowance3.data
        if edit_form.employment_status.data == "Resigned":
            employee_to_edit.date_resigned = date.today().strftime("%Y-%m-%d-%a")
        else:
            employee_to_edit.date_resigned = "-"

        db.session.commit()
        return redirect(url_for("employees"))
    return render_template("employees_input.html", form=edit_form)


@app.route("/employee_delete/<int:employee_index>", methods=["Get", "Post"])
@admin_only
@login_required
def employee_delete(employee_index):
    employee_to_delete = EmployeeProfileTable.query.get(employee_index)
    db.session.delete(employee_to_delete)
    db.session.commit()
    return redirect(url_for('employees'))


# Payroll---------------------------------------------------------------
@app.route("/payroll", methods=["Get", "Post"])
@admin_only
@login_required
def payroll():
    with create_engine(uri).connect() as cnx:
        raw = pd.read_sql_table(
            table_name="dispatch",
            con=cnx, index_col='dispatch_date',
            columns=['id', 'dispatch_date', 'wd_code', 'slip_no',
                     'area', 'destination', 'cbm', 'qty', 'drops', 'plate_no',
                     'driver', 'courier', 'forwarded_date'
                     ],
        )
    # check for unpaid dispatch
    unpaid_cnt = is_found(raw["forwarded_date"], "-")
    if unpaid_cnt > 0:
        df = raw.groupby("forwarded_date").get_group("-").sort_values("dispatch_date", ascending=False)  # group of unpaid dispatches

    else:
        df = raw.head(n=25).sort_values("dispatch_date", ascending=False)

    with create_engine(uri).connect() as cnx:
        strip_df = pd.read_sql_table(table_name="pay_strip", con=cnx)

    # check for unsettled
    unsettled = is_found(strip_df['date_settled'], '-')
    if unsettled > 0:
        pay_strip_df = strip_df.groupby("date_settled").get_group('-').sort_values('gen_date', ascending=True)
    else:
        pay_strip_df = strip_df.head(n=10).sort_values("date_settled", ascending=True)

    return render_template("payroll.html", unpaid_df=df, pay_strip_df=pay_strip_df, unpaid_cnt=unpaid_cnt)


@app.route("/add_payroll", methods=["Get", "Post"])
@admin_only
@login_required
def add_payroll():
    # step0: get fresh dispatch data
    # step1: group unpaid dispatch
    # step2: re-arrange unpaid dispatch group into index = wd_code and column labels = driver and courier
    # step3: create paystrip per column labels (or per employee)

    # step0
    with create_engine(uri).connect() as cnx:
        raw = pd.read_sql_table(
            table_name="dispatch",
            con=cnx, index_col='dispatch_date',
        )

    # step1
    unpaid_df = raw.groupby("forwarded_date").get_group("-")  # group of unpaid dispatches
    df1 = unpaid_df.pivot_table(values="slip_no", index=["wd_code"], columns=["driver"], aggfunc="count")
    df2 = unpaid_df.pivot_table(values="slip_no", index=["wd_code"], columns=["courier"], aggfunc="count")

    # step2
    df3 = pd.concat([df1, df2], axis=0).groupby(level=0).sum().fillna(0)

    # step3
    # initialize code variables
    normal = 0
    reg_hol = 0
    no_sp_hol = 0
    wk_sp_hol = 0
    rd = 0

    # iterate each employee on the column label
    for col in df3.columns:
        emp = EmployeeProfileTable.query.filter_by(full_name=col).first()
        for index in df3.index:
            if index == "normal":
                normal = df3.at[index, emp.full_name]
            elif index == "reg_hol":
                reg_hol = df3.at[index, emp.full_name]
            elif index == "no_sp_hol":
                no_sp_hol = df3.at[index, emp.full_name]
            elif index == "wk_sp_hol":
                wk_sp_hol = df3.at[index, emp.full_name]
            elif index == "rd":
                rd = df3.at[index, emp.full_name]

        # attendance computation
        equiv_wd = normal + (reg_hol * 2) + (no_sp_hol * 1.3) + (wk_sp_hol * 1) + (rd * 1.25)
        total_pay = (equiv_wd * emp.basic) + emp.allowance1 + emp.allowance2 + emp.allowance3

        # deduction (c.a remaining)
        if not emp.ca_remaining == 0:
            test = emp.ca_remaining - emp.ca_deduction
            if test <= 0:
                emp.ca_remaining = 0,
                emp.ca_deduction = emp.ca_remaining
                db.session.commit()
        total_deduction = emp.ca_deduction + emp.sss_prem + emp.philhealth_prem + emp.pag_ibig_prem

        # net pay
        net_pay = total_pay - total_deduction

        # money transfer and others
        transferred_amt1 = net_pay
        transferred_amt2 = 0
        carry_over_next_month = 0
        carry_over_past_month = 0

        # dispatch ids for each employee
        dispatch_ids = []
        if not unpaid_df[unpaid_df.driver == emp.full_name].empty:
            driver_group = unpaid_df.groupby('driver').get_group(emp.full_name)
            dispatch_ids = driver_group.id.tolist()
        elif not unpaid_df[unpaid_df.courier == emp.full_name].empty:
            courier_group = unpaid_df.groupby('courier').get_group(emp.full_name)
            dispatch_ids = courier_group.id.tolist()

        # update paystrip table
        new_strip = PayStripTable(
            date_settled="-",
            start_date=unpaid_df.index.min(),
            end_date=unpaid_df.index.max(),
            employee_name=emp.full_name,
            employee_id=emp.employee_id,
            # attendance
            normal=int(normal),
            reg_hol=int(reg_hol),
            no_sp_hol=int(no_sp_hol),
            wk_sp_hol=int(wk_sp_hol),
            rd=int(rd),
            equiv_wd=equiv_wd,
            # pay
            basic=emp.basic,
            allowance1=emp.allowance1,
            allowance2=emp.allowance2,
            allowance3=emp.allowance3,
            pay_adj=0,
            pay_adj_reason="-",
            # deduction
            cash_adv=emp.cash_adv,
            ca_date=emp.ca_date,
            ca_deduction=emp.ca_deduction,
            ca_remaining=emp.ca_remaining,
            sss=emp.sss_prem,
            philhealth=emp.philhealth_prem,
            pag_ibig=emp.pag_ibig_prem,
            life_insurance=0,
            income_tax=0,
            # summary
            total_pay=total_pay,
            total_deduct=total_deduction,
            net_pay=net_pay,
            transferred_amt1=transferred_amt1,
            transferred_amt2=transferred_amt2,
            carry_over_next_month=carry_over_next_month,
            carry_over_past_month=carry_over_past_month,
            gen_date=datetime.today().strftime("%Y-%m-%d"),
            paid_by=current_user.full_name,
            dispatch_ids=str(dispatch_ids)
        )
        db.session.add(new_strip)
        db.session.commit()

        indexes = [row[1] for row in unpaid_df.itertuples()]
        for index in indexes:
            disp = DispatchTable.query.get(index)
            disp.forwarded_date = datetime.today().strftime("%Y-%m-%d")
            db.session.commit()

    return redirect(url_for('payroll'))


@app.route("/adjust_paystrip/<int:strip_id>", methods=["Post", "Get"])
@admin_only
@login_required
def adj_paystrip():
    pass


@app.route("/delete_paystrip/<int:paystrip_id>", methods=["Get", "Post"])
@admin_only
@login_required
def delete_payroll(paystrip_id):
    payroll_to_delete = PayStripTable.query.get(paystrip_id)
    db.session.delete(payroll_to_delete)
    db.session.commit()
    return redirect(url_for("payroll"))


# tariff-----------------------------------------------------------------------------
@app.route("/tariff", methods=["Get", "Post"])
@admin_only
@login_required
def tariff():
    # get tariff data from database
    with create_engine(uri).connect() as cnx:
        df = pd.read_sql_table(table_name="tariff", con=cnx)
    return render_template("tariff_data.html", df=df)


@app.route("/add_tariff", methods=["Get", "Post"])
@admin_only
@login_required
def add_tariff():
    form = TariffForm()

    if form.validate_on_submit():
        new_tariff = Tariff(
            route=form.route.data.title(),
            area=form.area.data.title(),
            km=form.km.data,
            vehicle=form.vehicle.data.title(),
            cbm=form.cbm.data,
            rate=form.rate.data,
            diesel=form.diesel.data,
            update=form.update.data.strftime("%B %Y"),
            encoded_on=date.today().strftime("%Y-%m-%d-%a"),
            encoded_by=current_user.full_name
        )
        db.session.add(new_tariff)
        db.session.commit()
        return redirect(url_for('tariff'))
    return render_template('tariff_input.html', form=form)


@app.route("/edit_tariff/<int:tariff_id>", methods=["Get", "Post"])
@admin_only
@login_required
def edit_tariff(tariff_id):
    tariff_to_edit = Tariff.query.get(tariff_id)

    # pre-load form
    edit_form = TariffForm(
        route=tariff_to_edit.route,
        area=tariff_to_edit.area,
        km=tariff_to_edit.km,
        vehicle=tariff_to_edit.vehicle,
        cbm=tariff_to_edit.cbm,
        rate=tariff_to_edit.rate,
        diesel=tariff_to_edit.diesel,
        update=datetime.strptime(tariff_to_edit.update, "%B %Y")
    )
    if edit_form.validate_on_submit():
        tariff_to_edit.route = edit_form.route.data.title()
        tariff_to_edit.area = edit_form.area.data.title()
        tariff_to_edit.km = edit_form.km.data
        tariff_to_edit.vehicle = edit_form.vehicle.data.title()
        tariff_to_edit.cbm = edit_form.cbm.data
        tariff_to_edit.rate = edit_form.rate.data
        tariff_to_edit.diesel = edit_form.diesel.data
        tariff_to_edit.update = edit_form.update.data.strftime("%B %Y")
        tariff_to_edit.encoded_on = str(date.today().strftime("%Y-%m-%d-%a"))
        tariff_to_edit.encoded_by = current_user.full_name
        db.session.commit()
        return redirect(url_for('tariff'))
    return render_template("tariff_input.html", form=edit_form)


@app.route("/delete_tariff/<int:tariff_id>", methods=["Get", "Post"])
@admin_only
@login_required
def delete_tariff(tariff_id):
    tariff_to_delete = Tariff.query.get(tariff_id)
    db.session.delete(tariff_to_delete)
    db.session.commit()
    return redirect(url_for("tariff"))


@app.route("/invoice", methods=["Get", "Post"])
@admin_only
@login_required
def invoice():
    # get dispatch table
    with create_engine(uri).connect() as cnx:
        disp_df = pd.read_sql_table(
            table_name="dispatch",
            con=cnx,
        )
    # get invoice table
    with create_engine(uri).connect() as cnx:
        inv_df = pd.read_sql_table(
            table_name="invoice",
            con=cnx,
        )
    # check unpaid invoice
    unpaid_inv = is_found(inv_df["or_no"], "-")
    if unpaid_inv > 0:
        invoice_df = inv_df.groupby("or_no").get_group("-").sort_values("prepared_date", ascending=True)
    else:
        invoice_df = inv_df.head(5).sort_values("issued_on", ascending=True)

    # check for no invoice no
    inv_cnt = is_found(disp_df["invoice_no"], "-")
    if inv_cnt > 0:
        dispatch_df = disp_df.groupby("invoice_no").get_group("-").sort_values("plate_no", ascending=False)
    else:
        dispatch_df = 'none'

    return render_template('invoice_data.html', dispatch_df=dispatch_df, invoice_df=invoice_df, no_invoice_cnt=inv_cnt, )


@app.route("/create_invoice/", methods=["Get", "Post"])
@admin_only
@login_required
def add_invoice():

    # step0:
    with create_engine(uri).connect() as cnx:
        invoice_df = pd.read_sql_table(
            table_name="invoice",
            con=cnx,
        )
    with create_engine(uri).connect() as cnx:
        dispatch_df = pd.read_sql_table(
            table_name="dispatch",
            con=cnx,
        )
    invoice_list = create_invoice(invoice_df, dispatch_df)
    for invoice_item in invoice_list:
        new_invoice = Invoice(
            invoice_series=invoice_item['invoice_series'],
            invoice_no=invoice_item['invoice_no'],
            slip_nos=invoice_item['slip_nos'],
            plate_no=invoice_item['plate_no'],
            dispatch_cnt=invoice_item['dispatch_cnt'],
            gross_pay=invoice_item['gross_pay'],
            less=invoice_item['less'],
            amount_due=invoice_item['amount_due'],
            paid=invoice_item['paid'],
            or_no=invoice_item['or_no'],
            issued_on=invoice_item['issued_on'],
            prepared_date=invoice_item['prepared_date'],
            prepared_by=invoice_item['prepared_by'],
            dispatch_ids=invoice_item['dispatch_ids'],
        )
        db.session.add(new_invoice)
        db.session.commit()

        # update invoice number on dispatch database
        dispatch_ids = get_int_ids(invoice_item['dispatch_ids'])
        for num in dispatch_ids:
            dispatch_to_update = DispatchTable.query.get(num)
            dispatch_to_update.invoice_no = invoice_item['invoice_no']
            db.session.commit()

    return redirect(url_for('invoice'))


@app.route("/print_invoice/<int:invoice_id>", methods=["Post", "Get"])
@admin_only
@login_required
def print_invoice(invoice_id):
    # step1: get invoice target invoice
    invoice_to_print = Invoice.query.get(invoice_id)
    ids = get_int_ids(invoice_to_print.dispatch_ids)
    gross_pay = invoice_to_print.gross_pay
    less = invoice_to_print.less
    amount_due = invoice_to_print.amount_due
    inv_no = invoice_to_print.invoice_no
    inv_date = date.today()

    # step2: get fresh copy of dispatch
    with create_engine(uri).connect() as cnx:
        df = pd.read_sql_table(table_name="dispatch", con=cnx,)

    # step3: retrieve dispatch with the following ids]
    print_this = df[df.id.isin(ids)]
    amt_in_words = num2words(amount_due)
    in_words = amt_in_words.title() + ' pesos'

# later use
#
#     # using FPDF-------------------------------------------------------------------------------------------------
#     # create object
#     pdf = PDF('P', 'mm', 'A4')
#     # get total page numbers
#     pdf.alias_nb_pages()
#     # metadata
#     pdf.set_title(f'{inv_no}')
#     pdf.set_author('Gaspar Mamac')
#     # set auto page break
#     pdf.set_auto_page_break(auto=True, margin=15)
#     # add page
#     pdf.add_page()
#
#     # Company
#     pdf.set_font('helvetica', 'B', 12)
#     pdf.cell(0, 8, 'Mamac Logistics Services', ln=1, border=0)
#     # address
#     pdf.set_font('helvetica', '', 8)
#     pdf.set_text_color(169, 169, 169)
#     pdf.cell(0, 5, "Blk 3, Lot 9, Lulu Village, Brgy. R.Castillo Agdao District", ln=1, border=0)
#     pdf.cell(0, 5, "Cellphone#: 0948-6877234 / 0923-6003604 /0965-2965333 Tel#: (082)228-5232", ln=1, border=0)
#
#     # line break
#     pdf.set_font('helvetica', 'B', 12)
#     pdf.set_fill_color(169, 169, 169)
#     pdf.set_text_color(255, 255, 255)
#     pdf.cell(0, 10, "BILLING STATEMENT", border=0, ln=1, align='C', fill=1)
#
#     # bill to
#     pdf.set_font('helvetica', '', 8)
#     pdf.set_text_color(0, 0, 0)
#     pdf.cell(15, 6, 'Bill to: ', ln=0, border=0)
#     # customer
#     pdf.set_font('helvetica', 'B', 8)
#     pdf.cell(115, 6, 'LBC Expres Inc.', ln=0, border=0)
#     # invoice no
#     pdf.set_font('helvetica', '', 8)
#     pdf.cell(20, 6, 'Invoice no: ', border=0)
#     # actual invoice#
#     pdf.set_font('helvetica', 'B', 8)
#     pdf.cell(25, 6, f'{inv_no}', ln=1, border=0)
#
#     pdf.set_font('helvetica', '', 8)
#     pdf.cell(15, 6, 'Address: ', ln=0, border=0)
#     pdf.cell(115, 6, "Km. 7, Lanang Davao City", ln=0, border=0)
#     pdf.cell(20, 6, "Invoice Date: ", ln=0, border=0)
#     pdf.cell(25, 6, f"{date.today()}", ln=1, border=0)
#
#     # line break
#     pdf.ln('20')
#
#     # dispatch from - to
#     pdf.cell(10, 6, "From: ", ln=0, border=0)
#     pdf.set_font('helvetica', 'B', 8)
#     pdf.cell(25, 6, f"{print_this.dispatch_date.min()}", ln=0, border=0)
#     pdf.set_font('helvetica', '', 8)
#     pdf.cell(10, 6, "To: ", ln=0, border=0)
#     pdf.set_font('helvetica', 'B', 8)
#     pdf.cell(25, 6, f"{print_this.dispatch_date.max()}", ln=1, border=0)
#
#     # table
#     header = ['Dispatch date', 'Slip no', 'Plate no', 'Area', 'Dropping point/s', 'Cbm', 'Qty', 'Drops', 'Rate']
#     # header
#     pdf.set_font('helvetica', 'B', 8)
#     pdf.cell(25, 6, 'Dispatch date',border=1)
#     pdf.cell(20, 6, 'Slip no', border=1)
#     pdf.cell(20, 6, 'Plate no', border=1)
#     pdf.cell(30, 6, 'Area', border=1)
#     pdf.cell(35, 6, 'Dropping point/s', border=1)
#     pdf.cell(12, 6, 'Cbm', border=1)
#     pdf.cell(12, 6, 'Qty', border=1)
#     pdf.cell(12, 6, 'Drop/s', border=1)
#     pdf.cell(25, 6, 'Amount', border=1, ln=1)
#
#     # data
#     pdf.set_font('helvetica', '', 8)
#     for row in print_this.itertuples():
#         pdf.cell(25, 6, row[2], border=1)
#         pdf.cell(20, 6, row[4], border=1)
#         pdf.cell(20, 6, row[16], border=1)
#         pdf.cell(30, 6, row[6], border=1)
#         pdf.cell(35, 6, row[7], border=1)
#         pdf.cell(12, 6, str(row[11]), border=1)
#         pdf.cell(12, 6, str(row[12]), border=1)
#         pdf.cell(12, 6, str(row[13]), border=1)
#         pdf.cell(25, 6, str(row[15]), border=1, ln=1)
#     # summary
#     pdf.cell(142, 6, border=1)
#     pdf.cell(24, 6, 'Gross', border=1)
#     pdf.cell(25, 6, str(gross_pay), border=1, ln=1)
#     pdf.cell(142, 6, border=1)
#     pdf.cell(24, 6, 'Less', border=1)
#     pdf.cell(25, 6, str(less), border=1, ln=1)
#     pdf.cell(142, 6, border=1)
#     pdf.cell(24, 6, 'Amount due', border=1)
#     pdf.set_font('helvetica', 'B', 8)
#     pdf.cell(25, 6, str(amount_due), border=1, ln=1)
#
#     # amount in words
#     pdf.set_font('helvetica', '', 8)
#     pdf.cell(40, 6, 'Amount due in words:', ln=1)
#     pdf.set_font('helvetica', 'B', 8)
#     pdf.cell(40, 6, in_words, ln=1)
#
#     # payable to
#     pdf.set_font('helvetica', 'I', 8)
#     pdf.cell(45, 6, 'Please make all checks payable to:', ln=0)
#     pdf.set_font('helvetica', 'B', 8)
#     pdf.cell(40, 6, ' Mr. Gaspar Q. Mamac', ln=1)
#
#     # approve by (delete later)
#     pdf.ln(10)
#     pdf.set_font('helvetica', '', 8)
#     pdf.cell(130, 6, 'Checked and Approved by:', ln=0, border=0)
#     pdf.cell(35, 6, 'Received by:', ln=1, border=0)
#     pdf.set_font('helvetica', 'B', 8)
#     pdf.cell(130, 6, ' Mr. Nimrod Q. Mamac', ln=0)
#     pdf.cell(130, 6, '____________________', ln=1)
#     pdf.cell(130, 6, '', ln=0)
#     pdf.set_font('helvetica', 'I', 8)
#     pdf.cell(130, 1, '(Name/Signature/Date)', ln=1)
#     pdf.output(name=f"./invoices/{inv_no}.pdf")

    # attached pdf invoice to email
    # my_email = "mamaclogisticsservices441@gmail.com"
    # password = "!@#password"
    # msg = MIMEMultipart()
    # msg.attach(MIMEText(open(f"./invoices/2022-LWD-1.pdf", encoding='cp850').read()))
    # with smtplib.SMTP("smtp.gmail.com") as connection:
    #     connection.starttls()
    #     connection.login(user=my_email, password=password)
    #     connection.sendmail(
    #         from_addr=my_email,
    #         to_addrs="gasparmamac@gmail.com",
    #         msg=msg
    #     )

    return render_template('print_invoice.html', print_this=print_this, gross_pay=gross_pay, less=less, amount_due=amount_due, amt_in_words=in_words, inv_no=inv_no, inv_date=inv_date)


@app.route("/transaction", methods=["Post", "Get"])
@admin_only
@login_required
def transaction():
    # step0: get fresh copy of paystrip, maintenance, admin
    # step1: count each unsettled items
    # step2: create df for each table that has unsettled items
    # step3: display result

    # step0
    with create_engine(uri).connect() as cnx:
        df0 = pd.read_sql_table(
            table_name="dispatch",
            con=cnx,
        )
    with create_engine(uri).connect() as cnx:
        df1 = pd.read_sql_table(
            table_name="pay_strip",
            con=cnx,
        )
    with create_engine(uri).connect() as cnx:
        df2 = pd.read_sql_table(
            table_name="maintenance",
            con=cnx,
        )
    with create_engine(uri).connect() as cnx:
        df3 = pd.read_sql_table(
            table_name="admin",
            con=cnx,
        )
    with create_engine(uri).connect() as cnx:
        df4 = pd.read_sql_table(
            table_name="tariff",
            con=cnx,
        )

    # step1
    if not df1[df1.date_settled == "-"].empty:
        paystrip_grp = df1.groupby('date_settled').get_group('-')
        payroll_ttl = paystrip_grp.net_pay.sum()
        pay_cnt = len(df1.date_settled.tolist())

        # DIESEL computation
        # append list of ids to a single list
        list_of_id_list = [id_lst for id_lst in paystrip_grp.dispatch_ids]

        # combine list-of-list into a list of string
        cmb_id_list = []
        for id_list in list_of_id_list:
            cmb_id_list += id_list

        # convert string list to int list then, get only the unique value
        int_id_list = pd.Series(get_int_ids(cmb_id_list)).unique()
        unpaid_disp_df = df0[df0.id.isin(int_id_list)]

        # create dataframe for display
        diesel_df = unpaid_disp_df.groupby('area')['plate_no'].value_counts().unstack(fill_value=0)
        diesel_df.loc[:, 'Count'] = diesel_df.sum(axis=1, numeric_only=True)
        df4.set_index('area', inplace=True)
        diesel_df.loc[:, 'Budget'] = [df4.loc[row[0], 'diesel'] for row in diesel_df.itertuples()]
        diesel_df.loc[:, 'Total'] = diesel_df['Budget'] * diesel_df['Count']
        diesel_ttl = diesel_df.Total.sum()

    else:
        paystrip_grp = 'none'
        payroll_ttl = 0
        pay_cnt = 0
        diesel_df = 'none'
        diesel_ttl = 0

    if not df2[df2.date_settled == "-"].empty:
        maint_grp = df2.groupby('date_settled').get_group('-')
        maint_ttl = maint_grp.total_amt.sum()
        maint_cnt = len(df2.date_settled.tolist())
    else:
        maint_grp = 'none'
        maint_ttl = 0
        maint_cnt = 0

    if not df3[df3.date_settled == "-"].empty:
        admin_grp = df3.groupby('date_settled').get_group('-')
        admin_ttl = admin_grp.amount.sum()
        admin_cnt = len(df3.date_settled.tolist())
    else:
        admin_grp = 'none'
        admin_ttl = 0
        admin_cnt = 0

    # other contents
    trans_date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    grand_ttl = payroll_ttl + diesel_ttl + maint_ttl + admin_ttl
    amt_in_words = num2words(grand_ttl).title() + ' pesos'

    return render_template('transaction.html',
                           pay_cnt=pay_cnt, maint_cnt=maint_cnt, admin_cnt=admin_cnt,
                           paystrip_df=paystrip_grp, maint_df=maint_grp, admin_df=admin_grp, diesel_df=diesel_df,
                           payroll_ttl=payroll_ttl, diesel_ttl=diesel_ttl, maint_ttl=maint_ttl, admin_ttl=admin_ttl, grand_ttl=grand_ttl,
                           trans_date=trans_date, amt_in_words=amt_in_words)


@app.route("/add_transaction/<trans_date>", methods=['Post', 'Get'])
@admin_only
@login_required
def add_transaction(trans_date):
    # step0: get fresh copy of paystrip, maintenance, admin
    # step1: update date settled on paystrip, maint and admin tables
    # step2: update trasaction table

    # step0:
    with create_engine(uri).connect() as cnx:
        df1 = pd.read_sql_table(
            table_name="pay_strip",
            con=cnx,
        )
    with create_engine(uri).connect() as cnx:
        df2 = pd.read_sql_table(
            table_name="maintenance",
            con=cnx,
        )
    with create_engine(uri).connect() as cnx:
        df3 = pd.read_sql_table(
            table_name="admin",
            con=cnx,
        )

    # step1
    # update paystrip settled date
    if not df1[df1.date_settled == "-"].empty:
        paystrip_grp = df1.groupby('date_settled').get_group('-')
        paystrip_ids = paystrip_grp.id.tolist()
        for paystrip_id in paystrip_ids:
            paystrip_to_edit = PayStripTable.query.get(paystrip_id)
            paystrip_to_edit.date_settled = trans_date
            db.session.commit()
    else:
        paystrip_ids = []

    # update maintenance settled date
    if not df2[df2.date_settled == "-"].empty:
        maint_grp = df2.groupby('date_settled').get_group('-')
        maint_ids = maint_grp.id.tolist()
        for maint_id in maint_ids:
            maint_to_edit = MaintenanceTable.query.get(maint_id)
            maint_to_edit.date_settled = trans_date
            db.session.commit()
    else:
        maint_ids = []

    # update admin settled date
    if not df3[df3.date_settled == "-"].empty:
        admin_grp = df3.groupby('date_settled').get_group('-')
        admin_ids = admin_grp.id.tolist()
        for admin_id in admin_ids:
            admin_to_edit = AdminExpenseTable.query.get(admin_id)
            admin_to_edit.date_settled = trans_date
            db.session.commit()
    else: admin_ids = []

    # step5
    new_trans = Trasaction(
        trans_date=trans_date,
        paystrip_ids=str(paystrip_ids),
        maintenance_ids=str(maint_ids),
        admin_ids=str(admin_ids),
        by=current_user.full_name,
        on=datetime.today().strftime('%Y-%m-%d')
    )
    db.session.add(new_trans)
    db.session.commit()

    return redirect(url_for('transaction'))


@app.route("/recover_pw", methods=['Get', 'Post'])
@admin_only
@fresh_login_required
def recover_pw():
    form = ChangePwForm()
    msg = ''

    # show existing user email
    form.email.choices = [this_user.email for this_user in UserTable.query.order_by("last_name") ]

    # update use password
    if form.validate_on_submit():
        # check if entered pws are identical
        if form.pw.data == form.pw2.data:
            # create new hash and salted password
            new_pw = generate_password_hash(form.pw2.data, method="pbkdf2:sha256", salt_length=8)
            user_to_edit = UserTable.query.filter_by(email=form.email.data).first()
            user_to_edit.password = new_pw
            db.session.commit()
            msg = "Password change successful!"
            return render_template('recover.html', msg=msg)

        else:
            flash('Password did not match')
            return redirect(url_for('recover_pw'))
    return render_template('recover.html', form=form, msg=msg)


# ok_todo: 0 app view restriction
# todo: 1. O.R. number and amount update for lbc payment
# todo: 2.Pay adj routine
# todo: 3. Deduction routine (C.A, SSS)


if __name__ == "__main__":
    app.run(debug=False)
