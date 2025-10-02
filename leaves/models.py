from django.db import models
from django.contrib.auth.models import User
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
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Leave request for {self.employee} from {self.start_date} to {self.end_date}"

    class Meta:
        verbose_name = 'Leave Request'
        verbose_name_plural = 'Leave Requests'

    def save(self, *args, **kwargs):
        old_status = None
        if self.pk:
            old_instance = LeaveRequest.objects.get(pk=self.pk)
            old_status = old_instance.status

        status_changed_to_approved = self.status == 'approved' and old_status != 'approved'

        if status_changed_to_approved:
            with transaction.atomic():
                try:
                    balance = LeaveBalance.objects.select_for_update().get(
                        employee=self.employee,
                        leave_type=self.leave_type
                    )

                    requested_days = (self.end_date - self.start_date).days + 1

                    if balance.balance >= requested_days:
                        balance.balance -= Decimal(requested_days)
                        balance.save()
                    else:
                        self.status = 'rejected'
                        super().save(*args, **kwargs)

                except LeaveBalance.DoesNotExist:
                    self.status = 'rejected'
                    super().save(*args, **kwargs)