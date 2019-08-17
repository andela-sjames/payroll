from django.contrib import admin

# Register your models here.
from payapp.models import Report, Pay, PayRoll

# Register your models here.
admin.site.register(Report)
admin.site.register(Pay)
admin.site.register(PayRoll)