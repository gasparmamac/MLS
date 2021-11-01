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


