import string

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, FloatField, SelectField, RadioField, \
    TextAreaField
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
    extn_name = StringField("Extn name. (ex. Jr, Sr. III)")
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
    area = SelectField("Area")
    destination = StringField("Destination", validators=[DataRequired()])
    odo_start = IntegerField("Odo start (Km)")
    odo_end = IntegerField("Odo end (Km)")
    cbm = FloatField("Cbm", validators=[DataRequired()])
    qty = IntegerField("Qty", validators=[DataRequired()])
    drops = IntegerField("Drops", validators=[DataRequired()])
    rate = FloatField("Charge Rate", validators=[DataRequired()])
    plate_no = StringField("Plate no", validators=[DataRequired()])
    # driver = StringField("Driver", validators=[DataRequired()])
    driver = SelectField(u"Driver")
    # courier = StringField("Courier", validators=[DataRequired()])
    courier = SelectField("Courier")
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
    extn_name = SelectField("Extension.", choices=["", "Jr.", "Sr.", "I", "II", "III", "IV", "V"])
    birthday = DateField("Birthday", validators=[DataRequired()])
    gender = StringField("Gender", validators=[DataRequired()])
    # address
    address = TextAreaField("Address", validators=[DataRequired()])
    contact_no = StringField("Cellphone no.", validators=[DataRequired()])
    facebook = StringField("Facebook account")
    submit = SubmitField("Add Employee")


class EmployeeAdminEditForm(FlaskForm):
    # company related info
    employee_id = StringField("ID")
    date_hired = DateField("Date hired")
    employment_status = SelectField(
        "Status",
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


class PayStripForm(FlaskForm):
    start_date = DateField("From")
    end_date = DateField("To")
    employee_name = StringField("Name")
    employee_id = StringField("ID")
    # attendance
    normal = IntegerField("Normal")
    reg_hol = IntegerField("Regular holiday")
    no_sp_hol = IntegerField("Non working special holiday")
    wk_sp_hol = IntegerField("Working special holiday")
    rd = IntegerField("Rest day")
    # pay
    basic = FloatField("Basic")
    allowance1 = FloatField("Allowance1")
    allowance2 = FloatField("Allowance2")
    allowance3 = FloatField("Allowance3")
    # deduction
    cash_adv = FloatField("Cash advance")
    ca_date = DateField("C.A. date")
    ca_deduction = FloatField("C.A. deduction")
    ca_remaining = FloatField("C.A. remaining")
    sss = FloatField("SSS")
    philhealth = FloatField("PhilHealth")
    pag_ibig = FloatField("Pag-Ibig")
    life_insurance = FloatField("Life insurance")
    income_tax = FloatField("Income tax")
    # summary
    total_pay = FloatField("Gross pay")
    submit = SubmitField("Submit")


class TariffForm(FlaskForm):
    route = SelectField(
        'Route',
        choices=['Davao City', 'Gensan', 'Malita', 'Cotabato', 'Asuncion', 'Mati', 'CDO via Buda', 'CDO via Butuan'])
    area = StringField('Area')
    km = FloatField('Km')
    vehicle = StringField('Vehicle type')
    cbm = SelectField(
        'Cbm',
        choices=[3, 5, 8, 15, 25])
    rate = FloatField('Rate')
    update = DateField('LBC tariff released date')
    submit = SubmitField("Submit")


class CashAdvForm(FlaskForm):
    name = SelectField("Name")
    date = DateField("C.A. Date")
    amount = FloatField("Amount")
    deduction = FloatField("Deduction")


class TransactionForm(FlaskForm):
    pass









