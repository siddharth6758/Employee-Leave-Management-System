from django.urls import path
from employee.views import *

urlpatterns = [
    path("dashboard/", dashboard, name="employee_dashboard"),
    path("apply-delegate/", apply_delegate_handler, name="delegate_apply"),
]