from datetime import datetime

import pandas as pd
from flask_login import current_user
from sqlalchemy import create_engine
from main import EmployeeProfileTable, PayStripTable, db


class PayStrip:
    def __init__(self, employee, unpaid_df, grouped_df):
        self.grouped_df = grouped_df
        self.pay_day = "?"
        self.start_date = unpaid_df.index.min()
        self.end_date = unpaid_df.index.max()
        self.employee = employee.full_name
        self.employee_id = employee.id
        # attendance
        self.normal = 0
        self.reg_hol = 0
        self.no_sp_hol = 0
        self.wk_sp_hol = 0
        self.rd = 0
        self.equiv_wd = 0
        # pay
        self.basic = employee.basic
        self.allowance1 = employee.allowance1
        self.allowance2 = employee.allowance2
        self.allowance3 = employee.allowance3
        self.pay_adj = 0
        self.pay_adj_reason = "?"
        # deduction
        self.cash_adv = employee.cash_adv
        self.ca_date = employee.ca_date
        self.ca_deduction = employee.ca_deduction
        self.ca_remaining = employee.ca_remaining
        self.sss = employee.sss_prem
        self.philhealth = employee.philhealth_prem
        self.pag_ibig = employee.pag_ibig_prem
        self.life_insurance = 0
        self.income_tax = 0
        self.total_pay = 0
        self.total_deduction = 0
        self.net_pay = 0
        self.transferred_amt1 = 0
        self.transferred_amt2 = 0
        self.carry_over_next_month = 0
        self.carry_over_past_month = 0

        self.encoded_on = "?"
        self.encoded_by = "?"
        self.compute_total_pay()
        self.compute_deduction()
        self.compute_net_pay()

    def compute_total_pay(self):
        # iterate rows in each column
        for col in self.grouped_df.columns:
            for index in self.grouped_df.index:
                if index == "normal":
                    self.normal = self.grouped_df.loc[index, col]
                elif index == "reg_hol":
                    self.reg_hol = self.grouped_df.loc[index, col]
                elif index == "no_sp_hol":
                    self.no_sp_hol = self.grouped_df.loc[index, col]
                elif index == "wk_sp_hol":
                    self.wk_sp_hol = self.grouped_df.loc[index, col]
                elif index == "rd":
                    self.rd = self.grouped_df.loc[index, col]

        # attendance computation
        self.equiv_wd = self.normal + (self.reg_hol * 2) + (self.no_sp_hol * 1.3) + (self.wk_sp_hol * 1) + (self.rd * 1.25)
        self.total_pay = (self.equiv_wd * self.basic) + self.allowance1 + self.allowance2 + self.allowance3
        return self.total_pay

    def compute_deduction(self):
        # deduction (c.a remaining)
        if not self.ca_remaining == 0:
            self.ca_remaining -= self.ca_deduction
            if self.ca_remaining <= 0:
                self.ca_remaining = 0,
                self.ca_deduction = self.ca_remaining
        self.total_deduction = self.ca_deduction + self.sss + self.philhealth + self.pag_ibig + self.life_insurance + self.income_tax
        return self.total_deduction

    def compute_net_pay(self):
        # summary
        self.net_pay = self.total_pay - self.total_deduction
        return self.net_pay


def week_in_month(target_date):
    week_count_on_first_day = target_date.replace(day=1).isocalendar()[1]
    week_count_on_target_date = target_date.isocalendar()[1]
    num = week_count_on_target_date - week_count_on_first_day + 1
    return num


def is_found(list_to_check, char_to_find):
    cnt = 0
    for item in list_to_check:
        if item == char_to_find:
            cnt += 1
    if cnt > 0:
        return cnt
    else:
        return cnt


