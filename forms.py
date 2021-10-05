from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, FloatField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import DateField


class LoginForm(FlaskForm):
    user_name = StringField('User name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Register")


class DispatchForm(FlaskForm):
    dispatch_date = DateField("Dispatch date", validators=[DataRequired()])
    slip_no = StringField("Slip no", validators=[DataRequired()])
    route = StringField("Route", validators=[DataRequired()])
    cbm = FloatField("Cbm", validators=[DataRequired()])
    qty = IntegerField("Qty", validators=[DataRequired()])
    drops = IntegerField("Drops", validators=[DataRequired()])
    rate = FloatField("Rate", validators=[DataRequired()])
    plate_no = StringField("Plate no", validators=[DataRequired()])
    driver = StringField("Driver", validators=[DataRequired()])
    courier = StringField("Courier", validators=[DataRequired()])
    submit = SubmitField("Submit")

