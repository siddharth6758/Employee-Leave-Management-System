from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from leaves.forms import LeaveRequestForm
from leaves.models import LeaveRequest

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
    filter_type = request.GET.get('filter-type')
    context = {}
    if filter_type == "department-wise":
        leave_history = None # write aggregate login for employee.employee.department
        context["leave_history"] = leave_history
    else:
        leave_history = LeaveRequest.objects.all().order_by('-created')
        context["leave_history"] = leave_history
    print('\n\nLEAVER REPORT', leave_history)
    return render(request, 'leaves/leave_report.html', context=context)