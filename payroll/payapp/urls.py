from django.urls import path, re_path

from payapp import views

urlpatterns = [
    path('upload/', views.UploadReportView.as_view(), name='upload_report'),
    path('report/', views.ReportView.as_view(), name='get_report'),
    re_path(r'^payroll/(?P<report_id>[0-9]+)/$', views.GetPayRollByReportIdView.as_view(), name='get_payroll_id'),
    re_path(r'^report/(?P<report_id>[0-9]+)/$', views.GetReportByIdView.as_view(), name='get_report_id'),
]
