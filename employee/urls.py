from django.urls import path
from employee.views import *

urlpatterns = [
    path("dashboard/", dashboard, name="employee_dashboard"),
]