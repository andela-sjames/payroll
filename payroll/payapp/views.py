import calendar
import csv
import datetime
import io
import itertools
import json

from datetime import date, timedelta

from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Model
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView, View

from payapp.models import Pay, Report, PayRoll
from payapp.utils import normalize_date


class HomeView(TemplateView):
    """Homepage View defined here."""

    template_name = 'home.html'

    def get(self, request):
        return render(request, self.template_name)


class ReportView(TemplateView):
    """Report View defined here."""

    template_name = 'report.html'

    def get(self, request):
        return render(request, self.template_name)


class UploadReportView(View):
    """View defined to handle reports uploads and generating payrolls/"""

    def get_aggregate(self, grouped_pay, grp, employee_id):
        aggregate = (
        (
            employee_id, pay_period, 
            sum(hours for date, hours, job_group in daily_pay) * 20 if grp == "A" else sum(hours for date, hours, job_group in daily_pay) * 30) 
            for pay_period, daily_pay in grouped_pay
        )
        return list(aggregate)

    def two_weeks_pay_period(self, date):
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
    
    def format_time_string(self, date_string):
        d, m, y = list(map(int, date_string.split("/")))
        date_format = f"{y}-{m}-{d}"
        return date_format

    def get_or_create_report(self, report_id):
        try:
            return Report.objects.get(report_id=report_id), False
        except Report.DoesNotExist:
            report = Report(
                report_id = report_id
            )
            report.save()
            return report, True

    def post(self, request):
        csv_upload = request.FILES['csv_file']
        if not csv_upload.name.endswith('.csv'):
            return JsonResponse({
                "msg": "file should be CSV",
                "status": "failure",
            })

        data_set = csv_upload.read().decode('UTF-8')
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
        report, status = self.get_or_create_report(int(last_row[1]))
        if status:
            # proceed to create the pay model instances
            # this can be abstracted into a background process or
            # it's own service for scaling.
            for row in data:
                date_format = self.format_time_string(row[0])
                Pay.objects.create(
                    date = date_format,
                    hours = float(row[1]),
                    employee_id = int(row[2]),
                    job_group = row[3],
                    report = report
                )

            # start processing the payroll for future reference here
            cummulative_payroll = []
            report_query_set = report.pay.all()

            # retrieve a subset of data without the overhead of looping through instances
            employee_ids = set(report_query_set.values_list('employee_id', flat=True))

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
                    self.two_weeks_pay_period
                )
                aggregate = self.get_aggregate(grouped_pay, job_group, employee_id)
                cummulative_payroll = cummulative_payroll + aggregate

            # populate the DB here. 
            for data in cummulative_payroll:
                PayRoll.objects.create(
                    employee_id = data[0],
                    pay_period = data[1],
                    amount = data[2],
                    report = report
                )

            return JsonResponse({
                    "msg": "Report successfully created",
                    "status": "success", 
                    "report_id": report.report_id
                })
        else:
            return JsonResponse({
                "msg": f"Report {report.report_id} already exists", 
                "status": "failure"
            })


class GetPayRollByReportIdView(View):
    """View defined to get payroll report by ID."""

    def normalize_payroll(self, qs):
        for obj in qs:
            date = obj['pay_period']
            period = normalize_date(date, "payroll")
            obj['pay_period'] = period
            obj['amount'] = f"${obj['amount']}"
        return qs
    
    def get(self, request, *args, **kwargs):

        # cache this view for 1 hour
        cache_key = request.build_absolute_uri().split("?")[0]
        serialized_q = cache.get(cache_key)

        if not serialized_q:

            # query the DB for the report by id
            report_id = self.kwargs.get('report_id')
            try:
                report = Report.objects.get(report_id=report_id)
            except Report.DoesNotExist:
                return JsonResponse({
                    "msg": f"No Payroll report with id {report_id}",
                    "status": "failure", 
                })

            queryset = report.payroll.values('employee_id', 'pay_period', 'amount')
            queryset = self.normalize_payroll(queryset)
            serialized_q = json.dumps(list(queryset), cls=DjangoJSONEncoder)

        cache.set(cache_key, serialized_q)

        # return payroll at this point.
        return JsonResponse({
            "msg": "payroll loading",
            "status": "success", 
            "data": serialized_q
        })


class GetReportByIdView(View):
    """View defined to get pay report by id."""

    def normalize_report(self, qs):
        for obj in qs:
            date = obj['date']
            date = normalize_date(date, "report")
            obj['date'] = date
        return qs

    def get(self, request, *args, **kwargs):

        # cache is set to cache for 1 hour
        # from the seetings file.
        cache_key = request.build_absolute_uri().split("?")[0]
        serialized_q = cache.get(cache_key)

        if not serialized_q:
    
            # query the DB for the report by id
            report_id = self.kwargs.get('report_id')
            try:
                report = Report.objects.get(report_id=report_id)
            except Report.DoesNotExist:
                return JsonResponse({
                    "msg": f"No Pay report with id {report_id}",
                    "status": "failure", 
                })

            queryset = report.pay.values('date', 'hours', 'employee_id', 'job_group')
            queryset = self.normalize_report(queryset)
            serialized_q = json.dumps(list(queryset), cls=DjangoJSONEncoder)

        cache.set(cache_key, serialized_q)

        # return result at this point.
        return JsonResponse({
            "msg": "report loading",
            "status": "success", 
            "data": serialized_q
        })
