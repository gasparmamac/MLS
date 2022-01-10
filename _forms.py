from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, FloatField, SelectField, RadioField, \
    TextAreaField
from wtforms.validators import InputRequired, Length
from wtforms.fields.html5 import DateField


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Length(max=250, message='Input exceeds 250 characters')])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Length(max=250, message='Input exceeds 250 characters')])
    password = PasswordField("Password", validators=[InputRequired()])
    first_name = StringField("First name", validators=[InputRequired(), Length(max=250, message='Input exceeds 250 characters')])
    middle_name = StringField("Middle name", validators=[InputRequired(), Length(max=250, message='Input exceeds 250 characters')])
    last_name = StringField("Last Name", validators=[InputRequired(), Length(max=250, message='Input exceeds 250 characters')])
    extn_name = StringField("Extn name. (ex. Jr, Sr. III)", validators=[InputRequired(), Length(max=250, message='Input exceeds 250 characters')])
    submit = SubmitField("Register")


class DispatchForm(FlaskForm):
    dispatch_date = DateField("Dispatch date", validators=[InputRequired()])
    wd_code = SelectField("WD code", choices=[
        ("normal", "Normal Working day"),
        ("reg_hol", "Regular holiday"),
        ("no_sp_hol", "Non-working special holiday"),
        ("wk_sp_hol", "Working special holiday"),
        ("rd", "Rest day")
    ], validators=[InputRequired()])
    slip_no = StringField("Slip no", validators=[InputRequired(), Length(max=250, message='Input exceeds 250 characters')])
    area = SelectField("Area", validators=[InputRequired()])
    destination = StringField("Destination", validators=[InputRequired(), Length(max=250, message='Input exceeds 250 characters')])
    odo_start = IntegerField("Odo start (Km)", validators=[InputRequired()])
    odo_end = IntegerField("Odo end (Km)", validators=[InputRequired()])
    cbm = FloatField("Cbm", validators=[InputRequired()])
    qty = IntegerField("Qty", validators=[InputRequired()])
    drops = IntegerField("Drops", validators=[InputRequired()])
    rate = FloatField("Charge Rate", validators=[InputRequired()])
    plate_no = StringField("Plate no", validators=[InputRequired(), Length(max=250, message='Input exceeds 250 characters')])
    driver = SelectField("Driver", validators=[InputRequired()] )
    courier = SelectField("Courier", validators=[InputRequired()])
    submit = SubmitField("Submit")


class DispatchTableFilterForm(FlaskForm):
    filter = SelectField("Filter by:", choices=[
        ("dispatch_date", "Date dispatched"),
        ("encoded_on", "Date encoded")])
    date_start = DateField("From")
    date_end = DateField("To")
    submit = SubmitField("Apply filter")


class MaintenanceForm(FlaskForm):
    date = DateField("Date", validators=[InputRequired()])
    plate_no = StringField("Plate no", validators=[InputRequired(), Length(max=250, message='Input exceeds 250 characters')])
    type = SelectField("Type", choices=[
        "Repair",
        "Service",
        "Repair and service",
        "Tool/s",
        "Others"
    ], validators=[InputRequired()])
    comment = StringField("Expenses detail", validators=[InputRequired(), Length(max=250, message='Input exceeds 250 characters')])
    pyesa_amt = FloatField("Pyesa amt", validators=[InputRequired()])
    tools_amt = FloatField("Tools amt", validators=[InputRequired()])
    service_charge = FloatField("Service charge", validators=[InputRequired()])
    submit = SubmitField("Add record")


class MaintenanceFilterForm(FlaskForm):
    date_start = DateField("From")
    date_end = DateField("To")
    submit = SubmitField("Apply filter")


class AdminExpenseForm(FlaskForm):
    date = DateField("Date", validators=[InputRequired()])
    agency = StringField("Agency (ex. BIR, City Hall etc)", validators=[InputRequired(), Length(max=250, message='Input exceeds 250 characters')])
    office = StringField("Office (ex. Treasurer's office etc)", validators=[InputRequired(), Length(max=250, message='Input exceeds 250 characters')])
    frequency = StringField("Frequency (ex. Monthly, Yearly etc)", validators=[InputRequired(), Length(max=250, message='Input exceeds 250 characters')])
    description = StringField("Description", validators=[InputRequired(), Length(max=250, message='Input exceeds 250 characters')])
    amount = FloatField("Amount", validators=[InputRequired()])
    submit = SubmitField("Add record")


class AdminFilterForm(FlaskForm):
    date_start = DateField("From")
    date_end = DateField("To")
    submit = SubmitField("Apply filter")


class EmployeeEntryForm(FlaskForm):
    # personal info
    first_name = StringField("First name", validators=[InputRequired(), Length(max=250, message='Input exceeds 250 characters')])
    middle_name = StringField("Middle name", validators=[InputRequired(), Length(max=250, message='Input exceeds 250 characters')])
    last_name = StringField("Last name", validators=[InputRequired(), Length(max=250, message='Input exceeds 250 characters')])
    extn_name = SelectField("Extension.", choices=["", "Jr.", "Sr.", "I", "II", "III", "IV", "V"])
    birthday = DateField("Birthday", validators=[InputRequired()])
    gender = StringField("Gender", validators=[InputRequired(), Length(max=250, message='Input exceeds 250 characters')])
    # address
    address = TextAreaField("Address", validators=[InputRequired()])
    contact_no = StringField("Cellphone no.", validators=[InputRequired(), Length(max=250, message='Input exceeds 250 characters')])
    facebook = StringField("Facebook account", validators=[InputRequired(), Length(max=250, message='Input exceeds 250 characters')])
    submit = SubmitField("Add Employee")


class EmployeeAdminEditForm(FlaskForm):
    # company related info
    employee_id = StringField("ID", validators=[InputRequired(), Length(max=250, message='Input exceeds 250 characters')])
    date_hired = DateField("Date hired", validators=[InputRequired()])
    employment_status = SelectField(
        "Status",
        choices=["Contractual", "Provisional", "Regular", "Awol", "Resigned"], validators=[InputRequired()]
    )
    position = StringField("Position", validators=[InputRequired(), Length(max=250, message='Input exceeds 250 characters')])
    rank = StringField("Rank", validators=[InputRequired(), Length(max=250, message='Input exceeds 250 characters')])
    # benefits ids
    sss_no = StringField("SSS no", validators=[InputRequired(), Length(max=250, message='Input exceeds 250 characters')])
    philhealth_no = StringField("PhilHealth no", validators=[InputRequired(), Length(max=250, message='Input exceeds 250 characters')])
    pag_ibig_no = StringField("Pag-ibig no", validators=[InputRequired(), Length(max=250, message='Input exceeds 250 characters')])
    # benefits premium
    sss_prem = FloatField("SSS premium", validators=[InputRequired()])
    philhealth_prem = FloatField("PhilHealth premium", validators=[InputRequired()])
    pag_ibig_prem = FloatField("Pag-Ibig premium", validators=[InputRequired()])
    # compensation
    basic = FloatField("Basic premium", validators=[InputRequired()])
    allowance1 = FloatField("Allowance1", validators=[InputRequired()])
    allowance2 = FloatField("Allowance2", validators=[InputRequired()])
    allowance3 = FloatField("Allowance3", validators=[InputRequired()])
    submit = SubmitField("Add")


class PayStripForm(FlaskForm):
    start_date = DateField("From", validators=[InputRequired()])
    end_date = DateField("To", validators=[InputRequired()])
    employee_name = StringField("Name", validators=[InputRequired(), Length(max=250, message='Input exceeds 250 characters')])
    employee_id = StringField("ID", validators=[InputRequired(), Length(max=250, message='Input exceeds 250 characters')])
    # attendance
    normal = IntegerField("Normal", validators=[InputRequired()])
    reg_hol = IntegerField("Regular holiday", validators=[InputRequired()])
    no_sp_hol = IntegerField("Non working special holiday", validators=[InputRequired()])
    wk_sp_hol = IntegerField("Working special holiday", validators=[InputRequired()])
    rd = IntegerField("Rest day", validators=[InputRequired()])
    # pay
    basic = FloatField("Basic", validators=[InputRequired()])
    allowance1 = FloatField("Allowance1", validators=[InputRequired()])
    allowance2 = FloatField("Allowance2", validators=[InputRequired()])
    allowance3 = FloatField("Allowance3", validators=[InputRequired()])
    # deduction
    cash_adv = FloatField("Cash advance", validators=[InputRequired()])
    ca_date = DateField("C.A. date", validators=[InputRequired()])
    ca_deduction = FloatField("C.A. deduction", validators=[InputRequired()])
    ca_remaining = FloatField("C.A. remaining", validators=[InputRequired()])
    sss = FloatField("SSS", validators=[InputRequired()])
    philhealth = FloatField("PhilHealth", validators=[InputRequired()])
    pag_ibig = FloatField("Pag-Ibig", validators=[InputRequired()])
    life_insurance = FloatField("Life insurance", validators=[InputRequired()])
    income_tax = FloatField("Income tax", validators=[InputRequired()])
    # summary
    submit = SubmitField("Submit")


class AdjustPayment(FlaskForm):
    # pay adj reason 250 char only
    pass


class TariffForm(FlaskForm):
    route = SelectField(
        'Route',
        choices=['Davao City', 'Gensan', 'Malita', 'Cotabato', 'Asuncion', 'Mati', 'CDO via Buda', 'CDO via Butuan'], validators=[InputRequired()])
    area = StringField('Area', validators=[InputRequired(), Length(max=250, message='Input exceeds 250 characters')])
    km = FloatField('Km', validators=[InputRequired()])
    vehicle = StringField('Vehicle type', validators=[InputRequired(), Length(max=250, message='Input exceeds 250 characters')])
    cbm = SelectField(
        'Cbm',
        choices=[3, 5, 8, 15, 25], validators=[InputRequired()])
    rate = FloatField('Rate', validators=[InputRequired()])
    update = DateField('LBC tariff released date', validators=[InputRequired()])
    submit = SubmitField("Submit")


class CashAdvForm(FlaskForm):
    name = SelectField("Name", validators=[InputRequired()])
    date = DateField("C.A. Date", validators=[InputRequired()])
    amount = FloatField("Amount", validators=[InputRequired()])
    deduction = FloatField("Deduction", validators=[InputRequired()])














