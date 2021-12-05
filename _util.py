from datetime import datetime

import pandas as pd
from sqlalchemy import create_engine
from main import PayStripTable, EmployeeProfileTable, db


def week_in_month(target_date):
    week_count_on_first_day = target_date.replace(day=1).isocalendar()[1]
    week_count_on_target_date = target_date.isocalendar()[1]
    num = week_count_on_target_date - week_count_on_first_day + 1
    return num


def create_pay_strip(main_df, grouped_df):

    # iterate each column
    for col in grouped_df.columns:

        # unpack multi-column tuple
        (a, first_name) = col

        # query employee profile from data base
        employee = EmployeeProfileTable.query.filter_by(first_name=first_name).first()

        # extracting attendance
        for index in grouped_df.index:
            if index == "normal":
                normal = grouped_df.loc[index, col]
            elif index == "reg_hol":
                reg_hol = grouped_df.loc[index, col]
            elif index == "no_sp_hol":
                no_sp_hol = grouped_df.loc[index, col]
            elif index == "wk_sp_hol":
                wk_sp_hol = grouped_df.loc[index, col]
            elif index == "rd":
                rd = grouped_df.loc[index, col]

        # attendance computation
        equiv_wd = normal+(reg_hol*2)+(no_sp_hol*1.3)+(wk_sp_hol*1)+(rd*1.25)

        # C.A. computation
        if not employee.benefits.ca_remaining == 0:
            ca_deduction = employee.benefits.ca_deduction
            ca_remaining = employee.benefits.ca_remaining - ca_deduction
            if ca_remaining < 0:
                ca_remaining = 0,
                ca_deduction = employee.benefits.ca_remaining

        # Income tax computation ->later nani
        income_tax = 0

        # Monthly deduction (2nd week of the month)
        last_pay_strip = PayStripTable.query.filter_by().first()
        if week_in_month(datetime.today()) <= 2:
            sss = employee.benefits.sss_prem
            philhealth = employee.benefits.philhealth_prem
            pag_ibig = employee.benefits.pag_ibig_prem
            life_insurance = employee.benefits.life_insurance

        # Total pay computation
        total_pay = (
                (equiv_wd*employee.compensation.basic)
                + employee.benefits.allowance1
                + employee.benefits.allowance2
                + employee.benefits.allowance3
        )

        # Total deduction computation
        total_deduct = (
            ca_deduction
            + employee.benefits.sss_prem
            + employee.benefits.philhealth_prem
            + employee.benefits.pag_ibig_prem
            + employee.benefits.life_insurance
            + income_tax
        )

        new_pay_strip = PayStripTable(
            # common data
            pay_day=datetime.today(),
            start_date=main_df.index.min(),
            end_date=main_df.index.max(),
            employee_name=employee.first_name.title(),
            employee_id=employee.company_related_info.employee_id.upper(),
            # attendance
            normal=normal,
            reg_hol=reg_hol,
            no_sp_hol=no_sp_hol,
            wk_sp_hol=wk_sp_hol,
            rd=rd,
            equiv_wd=equiv_wd,
            # pay
            basic=employee.compensation.basic,
            allowance1=employee.compensation.allowance1,
            allowance2=employee.compensation.allowance2,
            allowance3=employee.compensation.allowance3,
            # deduction
            cash_adv=employee.benefits.cash_adv,
            ca_date=employee.benefits.ca_date,
            ca_deduction=ca_deduction,
            ca_remaining=ca_remaining,
            sss=sss,
            philhealth=philhealth,
            pag_ibig=pag_ibig,
            life_insurance=life_insurance,
            income_tax=income_tax,
            # summary
            total_pay=total_pay,
            total_deduct=total_deduct,
            net_pay=total_pay-total_deduct,
            transferred_amt1=0,
            transferred_amt2=0,
            carry_over_next_month=0,
            carry_over_past_month=0
        )
        db.session.add(new_pay_strip)
        db.session.commit()


