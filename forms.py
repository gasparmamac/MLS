from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, FloatField, SelectField, RadioField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import DateField, DateTimeField


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    first_name = StringField("First name", validators=[DataRequired()])
    middle_name = StringField("Middle name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    submit = SubmitField("Register")


class DispatchForm(FlaskForm):
    dispatch_date = DateField("Dispatch date", validators=[DataRequired()])
    wd_code = SelectField("WD code", choices=[
        ("normal", "Normal Working day"),
        ("reg_hol", "Regular holiday"),
        ("no_sp_hol", "Non-working special holiday"),
        ("wk_sp_hol", "Working special holiday"),
        ("rd", "Rest day")
    ])
    slip_no = StringField("Slip no", validators=[DataRequired()])
    route = SelectField("Route", choices=[
        "Davao City",
        "CDO via Buda",
        "GenSan",
        "Malita",
        "Cotabato",
        "Asuncion",
        "Mati",
        "CDO via Butuan"
    ])
    area = StringField("Area", validators=[DataRequired()])
    odo_start = IntegerField("Odo start (Km)")
    odo_end = IntegerField("Odo end (Km)")
    cbm = FloatField("Cbm", validators=[DataRequired()])
    qty = IntegerField("Qty", validators=[DataRequired()])
    drops = IntegerField("Drops", validators=[DataRequired()])
    rate = FloatField("Rate", validators=[DataRequired()])
    plate_no = StringField("Plate no", validators=[DataRequired()])
    driver = StringField("Driver", validators=[DataRequired()])
    courier = StringField("Courier", validators=[DataRequired()])
    submit = SubmitField("Submit")


class DispatchTableFilterForm(FlaskForm):
    filter = SelectField("Filter by:", choices=[
        ("dispatch_date", "Date dispatched"),
        ("encoded_on", "Date encoded")])
    date_start = DateField("From")
    date_end = DateField("To")
    submit = SubmitField("Apply filter")


class MaintenanceForm(FlaskForm):
    date = DateField("Date", validators=[DataRequired()])
    plate_no = StringField("Plate no", validators=[DataRequired()])
    type = SelectField("Type", choices=[
        "Repair",
        "Service",
        "Repair and service",
        "Tool/s",
        "Others"
    ])
    comment = StringField("Expenses detail", validators=[DataRequired()])
    pyesa_amt = FloatField("Pyesa amt")
    tools_amt = FloatField("Tools amt")
    service_charge = FloatField("Service charge")
    submit = SubmitField("Add record")


class MaintenanceFilterForm(FlaskForm):
    date_start = DateField("From")
    date_end = DateField("To")
    submit = SubmitField("Apply filter")


class AdminExpenseForm(FlaskForm):
    date = DateField("Date", validators=[DataRequired()])
    agency = StringField("Agency (ex. BIR, City Hall etc)")
    office = StringField("Office (ex. Treasurer's office etc)")
    frequency = StringField("Frequency (ex. Monthly, Yearly etc)")
    description = StringField("Description", validators=[DataRequired()])
    amount = FloatField("Amount")
    submit = SubmitField("Add record")


class AdminFilterForm(FlaskForm):
    date_start = DateField("From")
    date_end = DateField("To")
    submit = SubmitField("Apply filter")


class EmployeeEntryForm(FlaskForm):
    # personal info
    first_name = StringField("First name", validators=[DataRequired()])
    middle_name = StringField("Middle name", validators=[DataRequired()])
    last_name = StringField("Last name", validators=[DataRequired()])
    extn_name = StringField("Extension.  (N.A if not applicable)", validators=[DataRequired()])
    birthday = DateField("Birthday", validators=[DataRequired()])
    gender = StringField("Gender", validators=[DataRequired()])
    # address
    house_no = StringField("House no. (N.A if not applicable)", validators=[DataRequired()])
    lot_no = StringField("Lot no. (N.A if not applicable)", validators=[DataRequired()])
    block_no = StringField("Block no. (N.A if not applicable)", validators=[DataRequired()])
    sub_division = StringField("Sub division. (N.A if not applicable)", validators=[DataRequired()])
    purok = StringField("Purok. (N.A if not applicable)", validators=[DataRequired()])
    brgy = StringField("Brgy. (N.A if not applicable)", validators=[DataRequired()])
    district = StringField("District. (N.A if not applicable)", validators=[DataRequired()])
    city = StringField("City", validators=[DataRequired()])
    province = StringField("Province", validators=[DataRequired()])
    zip_code = StringField("ZIP Code", validators=[DataRequired()])
    submit = SubmitField("Add Employee")


class EmployeeAdminEditForm(FlaskForm):
    # company related info
    employee_id = StringField("ID")
    date_hired = DateField("Date hired")
    date_resigned = DateField("Date resigned")
    employment_status = SelectField(
        choices=["Contractual", "Provisional", "Regular", "Awol", "Resigned"]
    )
    position = StringField("Position")
    rank = StringField("Rank")
    # benefits ids
    sss_no = StringField("SSS no")
    philhealth_no = StringField("PhilHealth no")
    pag_ibig_no = StringField("Pag-ibig no")
    # benefits premium
    sss_prem = FloatField("SSS premium")
    philhealth_prem = FloatField("PhilHealth premium")
    pag_ibig_prem = FloatField("Pag-Ibig premium")
    # compensation
    basic = FloatField("Basic premium")
    allowance1 = FloatField("Allowance1")
    allowance2 = FloatField("Allowance2")
    allowance3 = FloatField("Allowance3")
    submit = SubmitField("Add")



