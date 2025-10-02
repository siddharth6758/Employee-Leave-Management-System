from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import LeaveRequest, LeaveBalance

class LeaveRequestForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Add Bootstrap classes or other attributes to your form fields
        self.fields['start_date'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
        self.fields['end_date'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
        self.fields['leave_type'].widget.attrs.update({'class': 'form-control'})
        self.fields['reason'].widget = forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})


    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'reason']

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        leave_type = cleaned_data.get('leave_type')

        # ensure all required fields are present
        if not all([start_date, end_date, leave_type, self.user]):
            return cleaned_data

        # date logic
        if leave_type != 'sick' and start_date < timezone.now().date():
            raise ValidationError("You cannot apply for leave in the past.")
        if end_date < start_date:
            raise ValidationError("The end date cannot be before the start date.")

        # check for overlapping leave requests
        overlapping_requests = LeaveRequest.objects.filter(
            employee=self.user,
            start_date__lte=end_date,
            end_date__gte=start_date
        ).exclude(pk=self.instance.pk) # exclude the current instance if editing an existing leave

        if overlapping_requests.exists():
            raise ValidationError("You already have a leave request that overlaps with these dates.")

        # check for sufficient leave balance
        try:
            balance_obj = LeaveBalance.objects.get(employee=self.user, leave_type=leave_type)
            available_balance = balance_obj.balance
        except LeaveBalance.DoesNotExist:
            available_balance = 0.0
        requested_days = (end_date - start_date).days + 1
        if requested_days > available_balance:
            raise ValidationError(
                f"Your balance for {leave_type.title()} Leave is insufficient. "
                f"You have {available_balance} days but are requesting {requested_days}."
            )
        return cleaned_data