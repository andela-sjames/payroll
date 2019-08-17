from django.conf.urls import include
from django.contrib import admin
from django.urls import path, re_path

import payapp.urls

from payapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.HomeView.as_view(), name="homepage"),
    re_path(r'^pay/', include('payapp.urls'))
]
