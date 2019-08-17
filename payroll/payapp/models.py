from datetime import datetime, time, timedelta, date

from django.db import models


class Report(models.Model):
    """Report model defined here.
    
    This model will be used to reference both the Pay model
    and payroll model via the related name provided by django ORM.
    """

    report_id = models.IntegerField(default=0)

    def __str__(self):
        return self.report_id


class Pay(models.Model):
    """Pay model defined to store the initial CSV file uploaded."""

    date = models.DateTimeField(default=datetime.now, blank=False)
    hours = models.FloatField()
    employee_id = models.IntegerField(default=0)
    job_group = models.CharField(default='', max_length=1)
    report = models.ForeignKey(Report, null=True, blank=True, on_delete=models.CASCADE, related_name="pay")

    def __str__(self):
        return self.employee_id


class PayRoll(models.Model):
    """PayRoll model defined to store the generated payroll report."""

    employee_id = models.IntegerField(default=0)
    pay_period = models.DateTimeField(default=datetime.now, blank=False)
    amount = models.FloatField()
    report = models.ForeignKey(Report, null=True, blank=True, on_delete=models.CASCADE, related_name="payroll")

    def __str__(self):
        return self.employee_id
