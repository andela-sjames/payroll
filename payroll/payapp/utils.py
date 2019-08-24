import csv
import io

from payapp.models import Report


def get_or_create_report(report_id):
    try:
        return Report.objects.get(report_id=report_id), False
    except Report.DoesNotExist:
        report = Report(
            report_id = report_id
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
