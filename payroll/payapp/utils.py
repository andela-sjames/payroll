def normalize_date(self, date, view):

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
