from datetime import datetime

from flask_login import current_user
from fpdf import FPDF


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


def create_invoice(invoice_df, dispatch_df):
    # steps
    # 1. filter no invoice from dispatch table
    # 2. regroup filtered dataframe per plate number
    # 3. create invoice no per plate number

    # step: 1
    grouped_df = dispatch_df.groupby('invoice_no').get_group("-")

    # step: 2
    plate_no_list = grouped_df.plate_no.unique().tolist()

    # step: 3
    year = datetime.today().strftime('%Y')
    inv_ser = len(invoice_df.invoice_series)
    if inv_ser == 0:
        inv_ser = 1
    else:
        inv_ser = int(invoice_df.invoice_series.max()) + 1

    invoice_list = []
    for plate_no in plate_no_list:
        # invoice
        ser_num = inv_ser
        invoice_no = f"{year}-{plate_no[:3]}-{inv_ser}"
        this_df = grouped_df.groupby("plate_no").get_group(plate_no)

        slip_nos = this_df.slip_no.tolist()
        dispatch_cnt = len(this_df.slip_no)
        gross_pay = this_df.rate.sum()
        less = round(gross_pay * 0.02, 2)
        amount_due = round(gross_pay * 0.98, 2)
        paid = 0
        or_no = '-'
        issued_on = '-'
        prepared_date = datetime.today().strftime("%Y-%m-%d")
        prepared_by = current_user.full_name
        dispatch_ids = this_df.id.tolist()
        invoice = {
            'invoice_series': ser_num,
            'invoice_no': invoice_no,
            'slip_nos': str(slip_nos),
            'plate_no': plate_no,
            'dispatch_cnt': dispatch_cnt,
            'gross_pay': gross_pay,
            'less': less,
            'amount_due': amount_due,
            'paid': paid,
            'or_no': or_no,
            'issued_on': issued_on,
            'prepared_date': prepared_date,
            'prepared_by': prepared_by,
            'dispatch_ids': str(dispatch_ids),
            }
        invoice_list.append(invoice)

    return invoice_list


def get_int_ids(str_id_list):
    int_ids = []
    str_num = ''

    for char in str_id_list:
        if char == '[':
            str_num = ''
        if char.isdigit():
            str_num += char
        elif char == ',':
            int_ids.append(int(str_num))
            str_num = ''
        elif char == ']':
            int_ids.append(int(str_num))
    return int_ids


def crete_paystrip():
    # step1:
    pass


class PDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', '', 8)
        self.set_text_color(169, 169, 169)
        self.cell(0, 6, f"Page {self.page_no()}/{{nb}}", align='R', ln=1)

        self.set_y(-10)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 6,
                  'This is a system generated report. For any concern, kindly contact us or '
                  'email at: gaspar.mamac@gmail.com',
                  align='C', ln=1)



