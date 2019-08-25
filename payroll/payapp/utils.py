import csv
import io
import itertools
import calendar

from payapp.models import Report


def get_aggregate(grouped_pay, grp, employee_id):
    aggregate = (
        (
            employee_id, pay_period, sum(
                hours for date, hours, job_group in daily_pay) * 20
            if grp == "A" else sum(
                hours for date, hours, job_group in daily_pay) * 30
        )
        for pay_period, daily_pay in grouped_pay
    )
    return list(aggregate)


def two_weeks_pay_period(date):
    # use 15 days to determine pay period
    # group by first day of the month and last day of the
    # month
    date = date[0]
    if 15 >= date.day:
        first_day = date.replace(day=1)
        return first_day
    else:
        last_day = date.replace(
            day=calendar.monthrange(date.year, date.month)[1]
        )
        return last_day


def get_or_create_report(report_id):
    try:
        return Report.objects.get(report_id=report_id), False
    except Report.DoesNotExist:
        report = Report(
            report_id=report_id
        )
        report.save()
        return report, True


def normalize_date(date, view):

    if view == "payroll":
        d, m, y = date.day, date.month, date.year
        date_format = f"{d}/{m}/{y}"
        if d is 1:
            end_date = f" - 15/{m}/{y}"
            return date_format + end_date
        else:
            start_date = f"16/{m}/{y} - "
            return start_date + date_format

    if view == "report":
        d, m, y = date.day, date.month, date.year
        return f"{d}/{m}/{y}"


def process_input(csv_data):

    data_set = csv_data.read().decode('UTF-8')
    io_string = io.StringIO(data_set)

    # Skip header, we do not need it, b/cos it's guaranteed.
    next(io_string)
    data = []
    # move on to the actual data
    for row in csv.reader(io_string, delimiter=",", quotechar="|"):
        # get the last row to know report_id
        columns = [row[0], row[1], row[2], row[3]]
        data.append(columns)

    last_row = data.pop()
    return data, get_or_create_report(int(last_row[1]))


def generate_payroll(report):
    # start processing the payroll for future reference here
    cummulative_payroll = []
    report_query_set = report.pay.all()

    # retrieve a subset of data without the overhead
    # of looping through instances
    employee_ids = set(
        report_query_set.values_list('employee_id', flat=True)
    )

    # use the ids to filter by dates
    for employee_id in employee_ids:
        # get pay period(s)
        daily_pay_query_set = report.pay.filter(
            employee_id=employee_id
        ).order_by(
            'date'
        ).values_list(
            'date', 'hours', 'job_group'
        )
        job_group = daily_pay_query_set[0][2]
        grouped_pay = itertools.groupby(
            daily_pay_query_set,
            two_weeks_pay_period
        )
        aggregate = get_aggregate(grouped_pay, job_group, employee_id)
        cummulative_payroll = cummulative_payroll + aggregate

    return cummulative_payroll
