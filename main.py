from flask import Flask, render_template, redirect, url_for, abort, flash
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, login_user, LoginManager, fresh_login_required, login_required, \
    current_user, logout_user
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_sqlalchemy import SQLAlchemy

from _forms import *
from _util import *

from datetime import datetime, date
from sqlalchemy import create_engine
import os

import pandas as pd

# pandas options
pd.options.display.float_format = '{:,.1f}'.format

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(12)
Bootstrap(app)

# Connect to database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lbc_dispatch.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Tables------------------------------------------------------------------

class UserTable(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    first_name = db.Column(db.String(100))
    middle_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    extn_name = db.Column(db.String(100))
    full_name = db.Column(db.String(100))
    dispatch = relationship("DispatchTable", back_populates="encoder")
    admin_exp = relationship("AdminExpenseTable", back_populates="encoder")
    maintenance = relationship("MaintenanceTable", back_populates="encoder")


class DispatchTable(UserMixin, db.Model):
    __tablename__ = "dispatch"
    id = db.Column(db.Integer, primary_key=True)
    dispatch_date = db.Column(db.String(100), nullable=False)
    wd_code = db.Column(db.String(100), nullable=False)
    slip_no = db.Column(db.String(100), nullable=False)
    route = db.Column(db.String(100), nullable=False)
    area = db.Column(db.String(250))
    destination = db.Column(db.String(100))
    odo_start = db.Column(db.Integer)
    odo_end = db.Column(db.Integer)
    km = db.Column(db.Float(precision=1))
    cbm = db.Column(db.String(100), nullable=False)
    qty = db.Column(db.String(100), nullable=False)
    drops = db.Column(db.String(100), nullable=False)
    std_rate = db.Column(db.Float(precision=1), nullable=False)
    rate = db.Column(db.Float(precision=1), nullable=False)
    plate_no = db.Column(db.String(100), nullable=False)
    driver = db.Column(db.String(100), nullable=False)
    courier = db.Column(db.String(100), nullable=False)
    pay_day = db.Column(db.String(100), nullable=False)
    invoice_no = db.Column(db.String(100))
    or_no = db.Column(db.String(100))
    or_amt = db.Column(db.Float(precision=1))
    encoded_on = db.Column(db.String(100), nullable=False)
    encoded_by = db.Column(db.String(100))
    encoder_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    encoder = relationship("UserTable", back_populates="dispatch")


class MaintenanceTable(UserMixin, db.Model):
    __tablename__ = "maintenance"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(100), nullable=False)
    plate_no = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    comment = db.Column(db.String(250), nullable=False)
    pyesa_amt = db.Column(db.Float(precision=1))
    tools_amt = db.Column(db.Float(precision=1))
    service_charge = db.Column(db.Float(precision=1))
    total_amt = db.Column(db.Float(precision=1))
    encoded_by = db.Column(db.String(100))
    encoder_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    encoder = relationship("UserTable", back_populates="maintenance")


class AdminExpenseTable(UserMixin, db.Model):
    __tablename__ = "admin"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(100), nullable=False)
    agency = db.Column(db.String(100), nullable=False)
    office = db.Column(db.String(100), nullable=False)
    frequency = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    amount = db.Column(db.Float(precision=1))
    encoded_by = db.Column(db.String(100))
    encoder_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    encoder = relationship("UserTable", back_populates="admin_exp")


class PayStripTable(UserMixin, db.Model):
    __tablename__ = "pay_strip"
    id = db.Column(db.Integer, primary_key=True)
    pay_day = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.String(100), nullable=False)
    end_date = db.Column(db.String(100), nullable=False)
    employee_name = db.Column(db.String(100), nullable=False)
    employee_id = db.Column(db.String(100), nullable=False)

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
    ca_date = db.Column(db.String(100))
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

    paid_on = db.Column(db.String(100))
    paid_by = db.Column(db.String(100))


class EmployeeProfileTable(UserMixin, db.Model):
    __tablename__ = "employee"
    id = db.Column(db.Integer, primary_key=True)

    # personal info
    first_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    extn_name = db.Column(db.String(100), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    birthday = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(100), nullable=False)
    contact_no = db.Column(db.String(100), nullable=False)
    facebook = db.Column(db.String(100))


    # address
    address = db.Column(db.String(100))

    # CompanyInfo
    employee_id = db.Column(db.String(100))
    date_hired = db.Column(db.String(100))
    date_resigned = db.Column(db.String(100))
    employment_status = db.Column(db.String(100))
    position = db.Column(db.String(100))
    rank = db.Column(db.String(100))

    # Benefits
    sss_no = db.Column(db.String(100))
    philhealth_no = db.Column(db.String(100))
    pag_ibig_no = db.Column(db.String(100))
    # benefits premiums
    sss_prem = db.Column(db.Float(precision=2))
    philhealth_prem = db.Column(db.Float(precision=2))
    pag_ibig_prem = db.Column(db.Float(precision=2))
    # deductions
    cash_adv = db.Column(db.Float(precision=2))
    ca_date = db.Column(db.String(100))
    ca_deduction = db.Column(db.Float(precision=2))
    ca_remaining = db.Column(db.Float(precision=2))

    # Compensation
    basic = db.Column(db.Float(precision=2))
    allowance1 = db.Column(db.Float(precision=2))
    allowance2 = db.Column(db.Float(precision=2))
    allowance3 = db.Column(db.Float(precision=2))

    encoded_on = db.Column(db.String(100))
    encoded_by = db.Column(db.String(100))


class Tariff(db.Model, UserMixin):
    __tablename__ = 'tariff'
    id = db.Column(db.Integer, primary_key=True)
    route = db.Column(db.String, nullable=True)
    area = db.Column(db.String(100), nullable=True)
    km = db.Column(db.Float(precision=1))
    vehicle = db.Column(db.String(100))
    cbm = db.Column(db.Float(precision=1))
    rate = db.Column(db.Float(precision=1))
    update = db.Column(db.String(50))
    encoded_on = db.Column(db.String(50))
    encoded_by = db.Column(db.String(10))







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
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function


# Login-logout-------------------------------------------------------
@app.route("/", methods=["Get", "Post"])
def home():

    return render_template("_index.html")


@app.route("/register", methods=["Get", "Post"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        # Confirm if the registrant is not on the database
        if UserTable.query.filter_by(email=form.email.data).first():
            print('Hello')
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
            password=hashed_and_salted_password
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
# @fresh_login_required
# @admin_only
def dispatch():
    # create table filter form
    form = DispatchTableFilterForm()

    # Get all dispatch data from database
    with create_engine('sqlite:///lbc_dispatch.db').connect() as cnx:
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
    return render_template("dispatch_data.html", form=form, df=sorted_df)


@app.route("/input_dispatch", methods=["Get", "Post"])
# @fresh_login_required
# @admin_only
@login_required
def input_dispatch():
    form = DispatchForm()
    form.driver.choices = [g.full_name for g in EmployeeProfileTable.query.order_by("last_name")]
    form.courier.choices = [g.full_name for g in EmployeeProfileTable.query.order_by("last_name")]
    form.area.choices = [a.area for a in Tariff.query.order_by("area")]

    if form.validate_on_submit():
        # todo: route function
        # todo: std rate function
        # Add new dispatch to database
        new_dispatch = DispatchTable(
            dispatch_date=form.dispatch_date.data.strftime("%Y-%m-%d-%a"),
            wd_code=form.wd_code.data,
            slip_no=form.slip_no.data,
            route="?",
            area=form.area.data.title(),
            destination=form.destination.data.title(),
            odo_start=form.odo_start.data,
            odo_end=form.odo_end.data,
            km=form.odo_end.data - form.odo_start.data,
            cbm=form.cbm.data,
            qty=form.qty.data,
            drops=form.drops.data,
            rate=form.rate.data,
            std_rate=0,
            plate_no=form.plate_no.data.upper(),
            driver=form.driver.data.title(),
            courier=form.courier.data.title(),
            encoded_on=date.today().strftime("%Y-%m-%d-%a"),
            encoded_by=current_user.first_name,
            encoder_id=current_user.id,
            pay_day='-',
            invoice_no='-',
            or_no='-',
            or_amt=0
        )
        db.session.add(new_dispatch)
        db.session.commit()
        return redirect(url_for("dispatch"))
    return render_template("dispatch_input.html", form=form)


@app.route("/edit_dispatch/<int:dispatch_id>", methods=["Get", "Post"])
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
        std_rate=0,
        plate_no=dispatch_to_edit.plate_no,
    )
    # choices for select field
    choices1 = ["?"]
    choices2 = ["?"]

    a = [g.full_name for g in EmployeeProfileTable.query.order_by("last_name")]
    b = [a.area for a in Tariff.query.order_by("area")]

    choices1 += a
    choices2 += b

    edit_form.driver.choices = choices1
    edit_form.courier.choices = choices1
    edit_form.area.choices = choices2

    route = "?"

    # load back edited form data to db
    if edit_form.validate_on_submit():
        dispatch_to_edit.dispatch_date = edit_form.dispatch_date.data.strftime("%Y-%m-%d-%a")
        dispatch_to_edit.wd_code = edit_form.wd_code.data
        dispatch_to_edit.slip_no = edit_form.slip_no.data
        dispatch_to_edit.route = route
        dispatch_to_edit.area = edit_form.area.data.title()
        dispatch_to_edit.destination = edit_form.destination.data.title()
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
        dispatch_to_edit.encoded_on = str(date.today().strftime("%Y-%m-%d-%a"))
        dispatch_to_edit.encoded_by = current_user.first_name
        db.session.commit()
        return redirect(url_for("dispatch"))
    return render_template("dispatch_input.html", form=edit_form)


@app.route("/delete_dispatch/<int:dispatch_id>", methods=["Get", "Post"])
def delete_dispatch(dispatch_id):
    dispatch_to_delete = DispatchTable.query.get(dispatch_id)
    db.session.delete(dispatch_to_delete)
    db.session.commit()
    return redirect(url_for("dispatch"))


# Maintenance expenses table---------------------------------------------
@app.route("/maintenance", methods=["Get", "Post"])
def maintenance():
    form = MaintenanceFilterForm()
    # Get all maintenance data from database
    with create_engine('sqlite:///lbc_dispatch.db').connect() as cnx:
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
            encoded_by=current_user.first_name.title()
        )
        db.session.add(new_record)
        db.session.commit()
        return redirect(url_for('maintenance'))
    return render_template("maintenance_input.html", form=form)


@app.route("/edit_maintenance/<int:maintenance_id>", methods=["Get", "Post"])
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
        maintenance_to_edit.encoded_by = current_user.first_name.title()
        db.session.commit()
        return redirect(url_for('maintenance'))
    return render_template("maintenance_input.html", form=edit_form)


@app.route("/delete_maintenance/<int:maintenance_id>", methods=["Get", "Post"])
def delete_maintenance(maintenance_id):
    maintenance_to_delete = MaintenanceTable.query.get(maintenance_id)
    db.session.delete(maintenance_to_delete)
    db.session.commit()
    return redirect(url_for('maintenance'))


# Admin expenses--------------------------------------------------------
@app.route("/admin", methods=["Get", "Post"])
def admin():
    form = AdminFilterForm()
    # Get all admin expenses data from database
    with create_engine('sqlite:///lbc_dispatch.db').connect() as cnx:
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
            encoded_by=current_user.first_name.title()
        )
        db.session.add(new_record)
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template("admin_input.html", form=form)


@app.route("/edit_admin/<int:admin_id>", methods=["Get", "Post"])
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
        admin_to_edit.encoded_by = current_user.first_name.title()
        db.session.commit()
        return redirect(url_for('employee'))
    return render_template("admin_input.html", form=edit_form)


@app.route("/delete_admin/<int:admin_id>", methods=["Get", "Post"])
def delete_admin(admin_id):
    admin_to_delete = AdminExpenseTable.query.get(admin_id)
    db.session.delete(admin_to_delete)
    db.session.commit()
    return redirect(url_for('admin'))


# Employee-------------------------------------------------------------
@app.route("/employee_list", methods=["Get", "Post"])
def employees():
    # Get all employees data from database
    with create_engine('sqlite:///lbc_dispatch.db').connect() as cnx:
        df = pd.read_sql_table(table_name="employee", con=cnx)
    return render_template("employees_data.html", df=df)


@app.route("/employee_add", methods=["Get", "Post"])
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
            employee_id="?",
            date_hired=date.today().strftime("%Y-%m-%d-%a"),
            date_resigned="?",
            employment_status="?",
            position="?",
            rank="?",
            # Benefits
            sss_no="?",
            philhealth_no="?",
            pag_ibig_no="?",
            # benefits premiums
            sss_prem=0,
            philhealth_prem=0,
            pag_ibig_prem=0,
            # deductions
            cash_adv=0,
            ca_date="?",
            ca_deduction=0,
            ca_remaining=0,
            # Compensation
            basic=0,
            allowance1=0,
            allowance2=0,
            allowance3=0,

        )
        db.session.add(new_employee)
        db.session.commit()
        return redirect(url_for("employees"))
    return render_template("employees_input.html", form=form)


@app.route("/employee_edit/<int:employee_index>", methods=["Get", "Post"])
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
        # print(edit_form.employment_status.data)
        if edit_form.employment_status.data == "Resigned":
            employee_to_edit.date_resigned = date.today().strftime("%Y-%m-%d-%a")
        else:
            employee_to_edit.date_resigned = ""

        db.session.commit()
        return redirect(url_for("employees"))
    return render_template("employees_input.html", form=edit_form)


@app.route("/employee_delete/<int:employee_index>", methods=["Get", "Post"])
def employee_delete(employee_index):
    employee_to_delete = EmployeeProfileTable.query.get(employee_index)
    db.session.delete(employee_to_delete)
    db.session.commit()
    return redirect(url_for('employees'))
    pass


# Payroll---------------------------------------------------------------
# todo: payroll paystrip
@app.route("/payroll", methods=["Get", "Post"])
def payroll():
    with create_engine('sqlite:///lbc_dispatch.db').connect() as cnx:
        raw = pd.read_sql_table(
            table_name="dispatch",
            con=cnx, index_col='dispatch_date',
            columns=['id', 'dispatch_date', 'wd_code', 'slip_no',
                     'area', 'destination', 'cbm', 'qty', 'drops', 'plate_no',
                     'driver', 'courier', 'pay_day'
                     ],
        )
    # check for unpaid dispatch
    unpaid_cnt = is_found(raw["pay_day"], "-")
    if unpaid_cnt > 0:
        paid = False
        df = raw.groupby("pay_day").get_group("-").sort_values("dispatch_date", ascending=False)  # group of unpaid dispatches

    else:
        paid = True
        df = raw.head(n=25).sort_values("dispatch_date", ascending=False)

    with create_engine('sqlite:///lbc_dispatch.db').connect() as cnx:
        strip_df = pd.read_sql_table(table_name="pay_strip", con=cnx)
        pay_strip_df = strip_df.head(n=25).sort_values("paid_on", ascending=False)

    return render_template("payroll.html", unpaid_df=df, pay_strip_df=pay_strip_df, paid=paid, unpaid_cnt=unpaid_cnt)


@app.route("/add_payroll", methods=["Get", "Post"])
def add_payroll():
    with create_engine('sqlite:///lbc_dispatch.db').connect() as cnx:
        raw = pd.read_sql_table(
            table_name="dispatch",
            con=cnx, index_col='dispatch_date',
        )
    unpaid_df = raw.groupby("pay_day").get_group("-")  # group of unpaid dispatches
    df1 = unpaid_df.pivot_table(values="slip_no", index=["wd_code"], columns=["driver"], aggfunc="count")
    df2 = unpaid_df.pivot_table(values="slip_no", index=["wd_code"], columns=["courier"], aggfunc="count")
    df3 = pd.concat([df1, df2], axis=0).groupby(level=0).sum().fillna(0)
    print(f"df3: {df3}")
    # initialize code variable
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

        # update paystrip table
        new_strip = PayStripTable(
            pay_day="?",
            start_date=unpaid_df.index.min(),
            end_date=unpaid_df.index.max(),
            employee_name=emp.full_name,
            employee_id=emp.employee_id,
            # attendance
            normal=normal,
            reg_hol=reg_hol,
            no_sp_hol=no_sp_hol,
            wk_sp_hol=wk_sp_hol,
            rd=rd,
            equiv_wd=equiv_wd,
            # pay
            basic=emp.basic,
            allowance1=emp.allowance1,
            allowance2=emp.allowance2,
            allowance3=emp.allowance3,
            pay_adj=0,
            pay_adj_reason="?",
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
            paid_on=datetime.today().strftime("%Y-%m-%d-%X"),
            paid_by=current_user.full_name
        )
        db.session.add(new_strip)
        db.session.commit()

    # update un-forwarded df
    indexes = [row[1] for row in unpaid_df.itertuples()]
    for index in indexes:
        disp = DispatchTable.query.get(index)
        disp.pay_day = datetime.today().strftime("%Y-%m-%d-%X")
        db.session.commit()
    print(indexes)

    return redirect(url_for('payroll'))


@app.route("/delete_paystrip/<int:paystrip_id>", methods=["Get", "Post"])
def delete_payroll(paystrip_id):
    payroll_to_delete = PayStripTable.query.get(paystrip_id)
    db.session.delete(payroll_to_delete)
    db.session.commit()
    return redirect(url_for("payroll"))


# tariff-----------------------------------------------------------------------------
@app.route("/tariff", methods=["Get", "Post"])
def tariff():
    # get tariff data from database
    with create_engine('sqlite:///lbc_dispatch.db').connect() as cnx:
        df = pd.read_sql_table(table_name="tariff", con=cnx)
    return render_template("tariff_data.html", df=df)


@app.route("/add_tariff", methods=["Get", "Post"])
def add_tariff():
    form = TariffForm()

    # get tariff data from database
    with create_engine('sqlite:///lbc_dispatch.db').connect() as cnx:
        df = pd.read_sql_table(table_name="tariff", con=cnx)

    if form.validate_on_submit():
        new_tariff = Tariff(
            route=form.route.data.title(),
            area=form.area.data.title(),
            km=form.km.data,
            vehicle=form.vehicle.data.title(),
            cbm=form.cbm.data,
            rate=form.rate.data,
            update=form.update.data.strftime("%B %Y"),
            encoded_on=date.today().strftime("%Y-%m-%d-%a"),
            encoded_by=current_user.full_name
        )
        db.session.add(new_tariff)
        db.session.commit()
        return redirect(url_for('tariff'))
    return render_template('tariff_input.html', form=form, df=df)


@app.route("/edit_tariff/<int:tariff_id>", methods=["Get", "Post"])
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
        update=datetime.strptime(tariff_to_edit.update, "%B %Y")
    )
    if edit_form.validate_on_submit():
        tariff_to_edit.route = edit_form.route.data.title()
        tariff_to_edit.area = edit_form.area.data.title()
        tariff_to_edit.km = edit_form.km.data
        tariff_to_edit.vehicle = edit_form.vehicle.data.title()
        tariff_to_edit.cbm = edit_form.cbm.data
        tariff_to_edit.rate = edit_form.rate.data
        tariff_to_edit.update = edit_form.update.data.strftime("%B %Y")
        tariff_to_edit.encoded_on = str(date.today().strftime("%Y-%m-%d-%a"))
        tariff_to_edit.encoded_by = current_user.full_name
        db.session.commit()
        return redirect(url_for('tariff'))
    return render_template("tariff_input.html", form=edit_form)


@app.route("/delete_tariff/<int:tariff_id>", methods=["Get", "Post"])
def delete_tariff(tariff_id):
    tariff_to_delete = Tariff.query.get(tariff_id)
    db.session.delete(tariff_to_delete)
    db.session.commit()
    return redirect(url_for("tariff"))


if __name__ == "__main__":
    app.run(debug=True)

