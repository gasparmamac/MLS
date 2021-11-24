from flask_login import UserMixin
from sqlalchemy.orm import relationship

from main import db


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


class EmployeeProfileTable(UserMixin, db.Model):
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
    company_related_info_id = db.Column(db.Integer, db.ForeignKey("company_related_info.id"))
    company_related_info = relationship("CompanyRelatedInfoTable", back_populates="employee", cascade="all, delete")

    benefits_id = db.Column(db.Integer, db.ForeignKey("benefits.id"))
    benefits = relationship("BenefitsTable", back_populates="employee", cascade="all, delete")

    compensation_id = db.Column(db.Integer, db.ForeignKey("compensation.id"))
    compensation = relationship("CompensationTable", back_populates="employee", cascade="all, delete")


class CompanyRelatedInfoTable(db.Model):
    __tablename__ = "company_related_info"
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(100))
    date_hired = db.Column(db.String(100))
    date_resigned = db.Column(db.String(100))
    employment_status = db.Column(db.String(100))
    position = db.Column(db.String(100))
    rank = db.Column(db.String(100))
    employee = relationship("EmployeeProfileTable", back_populates="company_related_info")


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
    # deductions
    cash_adv = db.Column(db.Float(precision=2))
    ca_date = db.Column(db.String(100))
    ca_deduction = db.Column(db.Float(precision=2))
    ca_remaining = db.Column(db.Float(precision=2))
    employee = relationship("EmployeeProfileTable", back_populates="benefits")


class CompensationTable(db.Model):
    __tablename__ = "compensation"
    id = db.Column(db.Integer, primary_key=True)
    basic = db.Column(db.Float(precision=2))
    allowance1 = db.Column(db.Float(precision=2))
    allowance2 = db.Column(db.Float(precision=2))
    allowance3 = db.Column(db.Float(precision=2))
    employee = relationship("EmployeeProfileTable", back_populates="compensation")


# Run only once
db.create_all()

