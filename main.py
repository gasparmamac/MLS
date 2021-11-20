from flask import Flask, render_template, redirect, url_for, abort, flash
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, login_user, LoginManager, fresh_login_required, login_required, \
    current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
# from forms import LoginForm, RegisterForm, DispatchForm, DispatchTableFilterForm, MaintenanceForm, \
#     MaintenanceFilterForm, AdminExpenseForm, AdminFilterForm
from forms import *
from datetime import datetime, date
from sqlalchemy.orm import relationship
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


# Database tables
class UserTable(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    first_name = db.Column(db.String(100))
    middle_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
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
    odo_start = db.Column(db.Integer)
    odo_end = db.Column(db.Integer)
    km = db.Column(db.Float(precision=1))
    cbm = db.Column(db.String(100), nullable=False)
    qty = db.Column(db.String(100), nullable=False)
    drops = db.Column(db.String(100), nullable=False)
    rate = db.Column(db.String(100), nullable=False)
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
    # children tables
    attendance = relationship("AttendanceTable", back_populates="strip")
    pay = relationship("PayTable", back_populates="strip")
    deduction = relationship("DeductionTable", back_populates="strip")
    summary = relationship("SummaryTable", back_populates="strip")


class AttendanceTable(db.Model):
    __tablename__ = "attendance"
    id = db.Column(db.Integer, primary_key=True)
    normal = db.Column(db.Integer)
    reg_hol = db.Column(db.Integer)
    no_sp_hol = db.Column(db.Integer)
    wk_sp_hol = db.Column(db.Integer)
    rd = db.Column(db.Integer)
    equiv_wd = db.Column(db.Float(precision=2))
    # parent table
    pay_strip_id = db.Column(db.Integer, db.ForeignKey("pay_strip.id"))
    strip = relationship("PayStripTable", back_populates="attendance")


class PayTable(db.Model):
    __tablename__ = "pay"
    id = db.Column(db.Integer, primary_key=True)
    basic = db.Column(db.Float(precision=2))
    allowance1 = db.Column(db.Float(precision=2))
    allowance2 = db.Column(db.Float(precision=2))
    allowance3 = db.Column(db.Float(precision=2))
    pay_adj = db.Column(db.Float(precision=2))
    pay_adj_reason = db.Column(db.String(250))
    # parent table
    pay_strip_id = db.Column(db.Integer, db.ForeignKey("pay_strip.id"))
    strip = relationship("PayStripTable", back_populates="pay")


class DeductionTable(db.Model):
    __tablename__ = "deduction"
    id = db.Column(db.Integer, primary_key=True)
    cash_adv = db.Column(db.Float(precision=2))
    ca_date = db.Column(db.String(100))
    ca_deduction = db.Column(db.Float(precision=2))
    ca_remaining = db.Column(db.Float(precision=2))
    sss = db.Column(db.Float(precision=2))
    philhealth = db.Column(db.Float(precision=2))
    pag_ibig = db.Column(db.Float(precision=2))
    life_insurance = db.Column(db.Float(precision=2))
    income_tax = db.Column(db.Float(precision=2))
    # parent table
    pay_strip_id = db.Column(db.Integer, db.ForeignKey("pay_strip.id"))
    strip = relationship("PayStripTable", back_populates="deduction")


class SummaryTable(db.Model):
    __tablename__ = "summary"
    id = db.Column(db.Integer, primary_key=True)
    total_pay = db.Column(db.Float(precision=2))
    total_deduct = db.Column(db.Float(precision=2))
    net_pay = db.Column(db.Float(precision=2))
    transferred_amt1 = db.Column(db.Float(precision=2))
    transferred_amt2 = db.Column(db.Float(precision=2))
    carry_over_next_month = db.Column(db.Float(precision=2))
    carry_over_past_month = db.Column(db.Float(precision=2))
    # parent table
    pay_strip_id = db.Column(db.Integer, db.ForeignKey("pay_strip.id"))
    strip = relationship("PayStripTable", back_populates="summary")


class EmployeeTable(UserMixin, db.Model):
    __tablename__ = "employee"
    id = db.Column(db.Integer, primary_key=True)
    # personal info
    first_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    extn_name = db.Column(db.String(100), nullable=False)
    birthday = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(100), nullable=False)
    # address
    house_no = db.Column(db.String(100))
    lot_no = db.Column(db.String(100))
    block_no = db.Column(db.String(100))
    sub_division = db.Column(db.String(100))
    purok = db.Column(db.String(100))
    brgy = db.Column(db.String(100))
    district = db.Column(db.String(100))
    city = db.Column(db.String(100))
    province = db.Column(db.String(100))
    zip_code = db.Column(db.String(100))
    # children tables
    company_related_info = relationship("CompanyRelatedInfoTable", back_populates="employee")
    benefits = relationship("BenefitsTable", back_populates="employee")
    compensation = relationship("CompensationTable", back_populates="employee")


class CompanyRelatedInfoTable(db.Model):
    __tablename__ = "company_related_info"
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(100))
    date_hired = db.Column(db.String(100))
    date_resigned = db.Column(db.String(100))
    employment_status = db.Column(db.String(100))
    position = db.Column(db.String(100))
    rank = db.Column(db.String(100))
    # parent table
    pay_strip_id = db.Column(db.Integer, db.ForeignKey("employee.id"))
    employee = relationship("EmployeeTable", back_populates="company_related_info")


class BenefitsTable(db.Model):
    __tablename__ = "benefits"
    id = db.Column(db.Integer, primary_key=True)
    sss_no = db.Column(db.String(100))
    philhealth_no = db.Column(db.String(100))
    pag_ibig_no = db.Column(db.String(100))
    # benefits premiums
    sss_prem = db.Column(db.Float(precision=2))
    philhealth_prem = db.Column(db.Float(precision=2))
    pag_ibig_prem = db.Column(db.Float(precision=2))
    pay_strip_id = db.Column(db.Integer, db.ForeignKey("employee.id"))
    employee = relationship("EmployeeTable", back_populates="benefits")


class CompensationTable(db.Model):
    __tablename__ = " compensation"
    id = db.Column(db.Integer, primary_key=True)
    basic = db.Column(db.Float(precision=2))
    allowance1 = db.Column(db.Float(precision=2))
    allowance2 = db.Column(db.Float(precision=2))
    allowance3 = db.Column(db.Float(precision=2))
    pay_strip_id = db.Column(db.Integer, db.ForeignKey("employee.id"))
    employee = relationship("EmployeeTable", back_populates="compensation")


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


# --------------------------------------------------Login-logout-------------------------------------------------------
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
        # Add new user to the database
        new_user = UserTable(
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


# -------------------------------------------------Dispatch table---------------------------------------------------
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
    sorted_df = df.head(n=20).sort_values("dispatch_date", ascending=False)

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
    if form.validate_on_submit():
        # Add new dispatch to database
        new_dispatch = DispatchTable(
            dispatch_date=form.dispatch_date.data.strftime("%Y-%m-%d-%a"),
            wd_code=form.wd_code.data,
            slip_no=form.slip_no.data,
            route=form.route.data.title(),
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
        dispatch_to_edit.dispatch_date = edit_form.dispatch_date.data.strftime("%Y-%m-%d-%a")
        dispatch_to_edit.wd_code = edit_form.wd_code.data
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


# ------------------------------------------------Maintenance expenses table------------------------------------------
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


# -------------------------------------------------Admin expenses----------------------------------------------------
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
        return redirect(url_for('admin'))
    return render_template("admin_input.html", form=edit_form)


@app.route("/delete_admin/<int:admin_id>", methods=["Get", "Post"])
def delete_admin(admin_id):
    admin_to_delete = AdminExpenseTable.query.get(admin_id)
    db.session.delete(admin_to_delete)
    db.session.commit()
    return redirect(url_for('admin'))


# ---------------------------------------------------------Employee---------------------------------------------------
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
        new_employee = EmployeeTable(
            # personal info
            first_name=form.first_name.data,
            middle_name=form.middle_name.data,
            last_name=form.last_name.data,
            extn_name=form.extn_name.data,
            birthday=form.birthday.data.strftime("%Y-%m-%d-%a"),
            gender=form.gender.data,
            # address
            house_no=form.house_no.data,
            lot_no=form.lot_no.data,
            block_no=form.block_no.data,
            sub_division=form.sub_division.data,
            purok=form.purok.data,
            brgy=form.brgy.data,
            district=form.district.data,
            city=form.city.data,
            province=form.province.data,
            zip_code=form.zip_code.data,
        )
        db.session.add(new_employee)
        db.session.commit()
        return redirect(url_for("employees"))
    return render_template("employees_input.html", form=form)


@app.route("/employee_edit/<int:employee_index>", methods=["Get", "Post"])
def employee_edit(employee_index):
    employee_to_edit = EmployeeTable.query.get(employee_index)
    # pre-load form
    edit_form = EmployeeEntryForm(
        first_name=employee_to_edit.first_name,
        middle_name=employee_to_edit.middle_name,
        last_name=employee_to_edit.last_name,
        extn_name=employee_to_edit.extn_name,
        birthday=datetime.strptime(employee_to_edit.birthday, "%Y-%m-%d-%a"),
        gender=employee_to_edit.gender,
        house_no=employee_to_edit.house_no,
        lot_no=employee_to_edit.lot_no,
        block_no=employee_to_edit.block_no,
        sub_division=employee_to_edit.sub_division,
        purok=employee_to_edit.purok,
        brgy=employee_to_edit.brgy,
        district=employee_to_edit.district,
        city=employee_to_edit.city,
        province=employee_to_edit.province,
        zip_code=employee_to_edit.zip_code
    )
    # reload edited form to db
    if edit_form.validate_on_submit():
        employee_to_edit.first_name = edit_form.first_name.data
        employee_to_edit.middle_name = edit_form.middle_name.data
        employee_to_edit.last_name = edit_form.last_name.data
        employee_to_edit.extn_name = edit_form.extn_name.data
        employee_to_edit.birthday = edit_form.birthday.data.strftime("%Y-%m-%d-%a")
        employee_to_edit.gender = edit_form.gender.data
        employee_to_edit.house_no = edit_form.house_no.data
        employee_to_edit.lot_no = edit_form.lot_no.data
        employee_to_edit.block_no = edit_form.block_no.data
        employee_to_edit.sub_division = edit_form.sub_division.data
        employee_to_edit.purok = edit_form.purok.data
        employee_to_edit.brgy = edit_form.brgy.data
        employee_to_edit.district = edit_form.district.data
        employee_to_edit.city = edit_form.city.data
        employee_to_edit.province = edit_form.province.data
        employee_to_edit.zip_code = edit_form.zip_code.data
        db.session.commit()
        return redirect(url_for("employees"))
    return render_template("employees_input.html", form=edit_form)


@app.route("/employee_delete/<int:employee_index>", methods=["Get", "Post"])
def employee_delete(employee_index):
    employee_to_delete = EmployeeTable.query.get(employee_index)
    db.session.delete(employee_to_delete)
    db.session.commit()
    return redirect(url_for('employees'))
    pass


# ---------------------------------------------------------Payroll----------------------------------------------------
@app.route("/payroll", methods=["Get", "Post"])
def payroll():
    with create_engine('sqlite:///lbc_dispatch.db').connect() as cnx:
        df = pd.read_sql_table(
            table_name="dispatch",
            con=cnx, index_col='dispatch_date',
            columns=['id', 'dispatch_date', 'wd_code', 'slip_no',
                     'route', 'area', 'cbm', 'qty', 'drops', 'plate_no',
                     'driver', 'courier', 'pay_day'
                     ]
        )
    df1 = df.groupby(['dispatch_date', 'driver']).count()
    df2 = df.groupby(['dispatch_date', 'courier']).count()
    sum_df = pd.concat(df1, df2).to_html(
        classes="table table-striped table-hover table-bordered table-sm",
    )
    # todo 2. construct individual payslip from the unpaid dispatch table above
    # todo 3. update dispatch and paystrip tables on click
    return render_template("payroll.html", df=df, sum_df=sum_df)













if __name__ == "__main__":
    app.run(debug=True)
