from decimal import Decimal
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db import models, transaction
from model_utils.models import TimeStampedModel

LEAVE_TYPES = (
    ('sick', 'Sick Leave'),
    ('casual', 'Casual Leave'),
    ('earned', 'Earned Leave'),
)

STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
)

class LeaveBalance(TimeStampedModel):
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = ('employee', 'leave_type')
        verbose_name = 'Leave Balance'
        verbose_name_plural = 'Leave Balances'


class LeaveRequest(TimeStampedModel):
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES, default='casual')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    approved_rejected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_rejected_leaves')
    approved_rejected_at = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Leave request for {self.employee} from {self.start_date} to {self.end_date}"

    class Meta:
        verbose_name = 'Leave Request'
        verbose_name_plural = 'Leave Requests'

    def save(self, *args, **kwargs):
        old_instance = None
        old_status = None
        requested_days = (self.end_date - self.start_date).days + 1
        # get old instance of leaverequest object
        with transaction.atomic():
            if not self.pk:
                if self.status in ["pending", "approved"]:
                    try:
                        balance = LeaveBalance.objects.get(
                            employee=self.employee,
                            leave_type=self.leave_type
                        )
                    except LeaveBalance.DoesNotExist:
                        raise ValidationError(f"No leave balance found for {self.leave_type} leave for user {self.employee.username}")
                    if balance.balance < requested_days:
                        raise ValidationError(f"Insufficient {self.leave_type} leave balance.")
                    balance.balance -= requested_days
                    balance.save()
            else:
                old_instance = LeaveRequest.objects.get(pk=self.pk)
                old_status = old_instance.status

                try:
                    balance = LeaveBalance.objects.select_for_update().get(
                        employee=self.employee,
                        leave_type=self.leave_type
                    )
                except LeaveBalance.DoesNotExist:
                    raise ValidationError(f"No leave balance found for {self.leave_type} leave for user {self.employee.username}")
                if self.status == "rejected" and old_status != "rejected":
                    # if the status is changed to rejected then add back the balance
                    try:
                        balance.balance += requested_days
                        balance.save()
                    except LeaveBalance.DoesNotExist:
                        raise ValidationError(f"No leave balance found for {self.leave_type} leave for user {self.employee.username}")
                elif self.status in ["pending", "approved"] and old_status == "rejected":
                    #if the status is changed from rejected to pending or approved then deduct the balance
                    if balance.balance < requested_days:
                        raise ValidationError(f"Insufficient {self.leave_type} leave balance.")
                    balance.balance -= requested_days
                    balance.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.status in ['approved', 'pending']:
            with transaction.atomic():
                try:
                    # lock the LeaveBalance row to prevent race conditions/deadlocks
                    balance = LeaveBalance.objects.select_for_update().get(
                        employee=self.employee,
                        leave_type=self.leave_type
                    )
                    leave_days = (self.end_date - self.start_date).days + 1
                    # add the days back to the balance
                    balance.balance += Decimal(leave_days)
                    balance.save()
                except LeaveBalance.DoesNotExist:
                    pass
                super().delete(*args, **kwargs)
        else:
            super().delete(*args, **kwargs)