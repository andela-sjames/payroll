import json

from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Model
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView, View

from payapp.models import Pay, Report, PayRoll
from payapp.utils import normalize_date, process_input, generate_payroll


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
    
    def format_time_string(self, date_string):
        d, m, y = list(map(int, date_string.split("/")))
        date_format = f"{y}-{m}-{d}"
        return date_format

    def post(self, request):
        csv_data = request.FILES['csv_file']
        if not csv_data.name.endswith('.csv'):
            return JsonResponse({
                "msg": "file should be CSV",
                "status": "failure",
            })

        data, report_status = process_input(csv_data)
        report, status = report_status
        if status:
            # proceed to create the pay model instances
            for row in data:
                date_format = self.format_time_string(row[0])
                Pay.objects.create(
                    date = date_format,
                    hours = float(row[1]),
                    employee_id = int(row[2]),
                    job_group = row[3],
                    report = report
                )

            payroll = generate_payroll(report)

            # populate the DB here. 
            for data in payroll:
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
        # from the settings file.
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
