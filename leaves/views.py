import csv
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from leaves.forms import LeaveRequestForm
from django.utils import timezone
from leaves.models import LeaveRequest
from employee.models import Delegation
from django.http import JsonResponse, StreamingHttpResponse

class Echo:
    def write(self, value):
        return value

@login_required(login_url='login')
def leave_request_handler(request):
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.employee = request.user
            try:
                leave_request.save()
            except Exception as e:
                form.add_error(None, e.message)
                return render(request,'leaves/leave_apply.html', {'form':form})
            return redirect('employee_dashboard')
        return render(request,'leaves/leave_apply.html', {'form':form})
    else:
        form = LeaveRequestForm()
        return render(request,'leaves/leave_apply.html', {'form':form})


@login_required(login_url='login')
def leave_request_status(request):
    user = request.user
    leave_requests_history = LeaveRequest.objects.filter(employee=user).order_by('-created')
    to_manager = user.employee.manager
    context = {
        "leave_request_history": leave_requests_history,
        "to_manager": to_manager if to_manager else '--'
    }
    return render(request, 'leaves/leave_status.html', context=context)


@login_required(login_url='login')
def leaves_report_handler(request):
    filter_type = request.GET.get('filter-type', 'all')
    context = {
        "department_filter": False
    }
    if filter_type == "department-wise":
        leave_history_qs = LeaveRequest.objects.select_related(
            'employee__employee__department'
        )
        leave_history = {}
        for leave in leave_history_qs:
            department = leave.employee.employee.department.name if leave.employee.employee.department else 'No Department'
            if department not in leave_history:
                leave_history[department] = []
            leave_history[department].append(leave)
        context["leave_history"] = leave_history
        context["department_filter"] = True
    elif filter_type == "all":
        leave_history = LeaveRequest.objects.all().order_by('-created')
        context["leave_history"] = leave_history
    return render(request, 'leaves/leave_report.html', context=context)

@login_required(login_url='login')
def download_leave_report_handler(request):
    leave_history = LeaveRequest.objects.select_related('employee').all().order_by('-created')
    header = ['Employee', 'Department', 'Leave Type', 'Start Date', 'End Date', 'Status', 'Reason', 'Approved By', 'Approved At']
    data_rows = [
        [
            leave.employee.username,
            leave.employee.employee.department.name if leave.employee.employee.department else 'No-Department',
            leave.get_leave_type_display(),
            leave.start_date,
            leave.end_date,
            leave.get_status_display(),
            leave.reason,
            leave.approved_rejected_by,
            leave.approved_rejected_at,
        ]
        for leave in leave_history
    ]
    all_rows = [header] + data_rows

    # use the csv module to write this list to the streaming buffer
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)

    response = StreamingHttpResponse(
        (writer.writerow(row) for row in all_rows),
        content_type="text/csv"
    )
    response['Content-Disposition'] = 'attachment; filename="leave_report.csv"'
    return response


@login_required(login_url='login')
def approve_leave(request):
    leave_id = request.POST.get('leave_id')
    if not leave_id:
        return JsonResponse({'success': False, 'error': 'Leave ID not provided.'}, status=400)

    try:
        delegate_user = Delegation.objects.filter(
            delegate=request.user,
            start_date__gte=timezone.now().date(),
            end_date__lte=timezone.now().date()
        )
        if request.user.employee.is_manager or delegate_user.exists():
            leave_request = LeaveRequest.objects.get(
                pk=leave_id
            )

            if leave_request.status == 'pending':
                leave_request.status = 'approved'
                leave_request.approved_rejected_by = request.user
                leave_request.approved_rejected_at = timezone.now()
                leave_request.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'This leave has already been actioned.'}, status=400)
        else:
            return JsonResponse({'success': False, 'error': 'You are not authorized to perform this action.'}, status=403)

    except LeaveRequest.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Leave request not found or you are not authorized.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required(login_url='login')
def reject_leave(request):
    leave_id = request.POST.get('leave_id')
    if not leave_id:
        return JsonResponse({'success': False, 'error': 'Leave ID not provided.'}, status=400)

    try:
        delegate_user = Delegation.objects.filter(
            delegate=request.user,
            start_date__gte=timezone.now().date(),
            end_date__lte=timezone.now().date()
        )
        if request.user.employee.is_manager or delegate_user.exists():
            leave_request = LeaveRequest.objects.get(
                pk=leave_id
            )

            if leave_request.status == 'pending':
                leave_request.status = 'rejected'
                leave_request.approved_rejected_by = request.user
                leave_request.approved_rejected_at = timezone.now()
                leave_request.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'This leave has already been actioned.'}, status=400)
        else:
            return JsonResponse({'success': False, 'error': 'You are not authorized to perform this action.'}, status=403)

    except LeaveRequest.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Leave request not found or you are not authorized.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)