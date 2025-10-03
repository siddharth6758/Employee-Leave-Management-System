from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from employee.models import  Delegation
from employee.forms import DelegationForm
from leaves.models import LeaveBalance, LeaveRequest, LEAVE_TYPES

#employee1 - emp@1234
#employee2 - emp2@1234
#manager - man@1234

@login_required(login_url='login')
def dashboard(request):
    user = request.user
    #get leave balance of the user
    leave_balances = LeaveBalance.objects.filter(employee=user).values('leave_type', 'balance')
    leave_balances = {i['leave_type']:float(i['balance']) for i in leave_balances}
    leave_balances = {type:leave_balances.get(type, 0.0) for type,_ in LEAVE_TYPES}
    context = {
        'leave_balance':leave_balances,
        'is_manager':user.employee.is_manager, #to check if user is manager
        'is_delegated_manager': False #set by default to false
    }

    #check if the employee is set as delegate manager for today
    today = timezone.now().date()
    active_delegation = Delegation.objects.filter(
        delegate=user,
        start_date__lte=today,
        end_date__gte=today
    ).first()
    #if set then get all the leave requests given to manager and show it to employee
    if active_delegation:
        context["is_delegated_manager"] = True
        delegated_requests = LeaveRequest.objects.filter(
            employee__employee__manager=active_delegation.manager, #get those requests given to delegated manager
            status='pending'
        )
        context["delegated_requests"] = delegated_requests

    #if user is manager
    if user.employee.is_manager:
        #get all leave requests pending for approval
        pending_leave_requests = LeaveRequest.objects.filter(
            employee__employee__manager=user,
            status="pending"
        )
        context["pending_leave_requests"] = pending_leave_requests
    return render(request, "dashboard.html", context=context)

@login_required(login_url='login')
def apply_delegate_handler(request):
    if request.method == 'POST':

        form = DelegationForm(request.POST)
        if form.is_valid():
            delegration_request = form.save(commit=False)
            delegration_request.manager = request.user
            try:
                delegration_request.save()
            except Exception as e:
                form.add_error(None, e.message)
                return render(request,'delegation.html', {'form':form})
            return redirect('employee_dashboard')
        return render(request,'delegation.html', {'form':form})
    else:
        form = DelegationForm(manager=request.user)
        return render(request,'delegation.html', {'form':form})