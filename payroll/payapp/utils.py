def get_aggregate(grouped_pay, grp, employee_id):
        aggregate = (
        (
            employee_id, pay_period, 
            sum(hours for date, hours, job_group in daily_pay) * 20 if grp == "A" else sum(hours for date, hours, job_group in daily_pay) * 30) 
            for pay_period, daily_pay in grouped_pay
        )
        return list(aggregate)

def two_weeks_pay_period(date):
    # use 15 days to determine pay period
    # group by first day of the month and last day of the 
    # month
    date = date[0]
    if 15 >= date.day:
        first_day = date.replace(day = 1)
        return first_day
    else:
        last_day = date.replace(day = calendar.monthrange(date.year, date.month)[1])
        return last_day

def format_time_string(date_string):
    d, m, y = list(map(int, date_string.split("/")))
    date_format = f"{y}-{m}-{d}"
    return date_format
