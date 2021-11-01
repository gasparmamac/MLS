

rate_dict = {'Nimrod': 450, 'Abe': 400, 'Archael': 350, 'Rommel': 400, 'Tete': 250}
diesel_dict = {'LWD-262': 300, 'YKV-852': 500}


# Salary and diesel rate matching
def rate_matcher(df):
    rate = []
    total = []
    for row in df.itertuples():
        if row[0] == 'Abe':
            total.append(row[1]*rate_dict['Abe'])
            rate.append(rate_dict['Abe'])
        elif row[0] == 'Rommel':
            total.append(row[1]*rate_dict['Rommel'])
            rate.append(rate_dict['Rommel'])
        elif row[0] == 'Nimrod':
            total.append(row[1]*rate_dict['Nimrod'])
            rate.append(rate_dict['Nimrod'])
        elif row[0] == 'Archael':
            total.append(row[1]*rate_dict['Archael'])
            rate.append(rate_dict['Archael'])
    return rate, total


def diesel_matcher(df):
    diesel_rate = []
    total = []
    for row in df.itertuples():
        if row[0] == 'LWD-262':
            diesel_rate.append(diesel_dict['LWD-262'])
            total.append(row[1]*diesel_dict['LWD-262'])
        elif row[0] == 'YKV-852':
            diesel_rate.append(diesel_dict['YKV-852'])
            total.append(row[1]*diesel_dict['YKV-852'])
    return diesel_rate, total

