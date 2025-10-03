from django.urls import path
from leaves.views import *

urlpatterns = [
    path('apply-leave-request/',leave_request_handler, name='apply_leave_request'),
    path('leave-status/',leave_request_status, name='leave_status'),
    path('leave-report/',leaves_report_handler, name='leave_report')
]