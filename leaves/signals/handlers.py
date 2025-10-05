from django.core.mail import send_mail
from django.dispatch import receiver
from django.conf import settings
from django.db.models.signals import post_save, pre_save
from leaves.models import LeaveRequest

@receiver(post_save, sender=LeaveRequest)
def send_leave_request_notification(sender, instance, created, **kwargs):
    if created:
        # mail for new leave request just created
        employee = instance.employee
        manager = employee.employee.manager

        if manager and manager.email:
            subject = f"New Leave Request from {employee.username}"
            message = (
                f"A new leave request has been submitted by {employee.username}.\n\n"
                f"Type: {instance.get_leave_type_display()}\n"
                f"Dates: {instance.start_date} to {instance.end_date}\n"
                f"Reason: {instance.reason}\n\n"
            )
            # send the email to the manager
            if manager.email:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[manager.email],
                    fail_silently=False,
                )

@receiver(pre_save, sender=LeaveRequest)
def send_approval_rejection_email(sender, instance, **kwargs):
    # when leave request is updated (approved/rejected)
    if instance.pk:
        old_request = LeaveRequest.objects.get(pk=instance.pk)
        # check if the status is updated
        if old_request.status != instance.status:
            if instance.status in ['approved', 'rejected']:
                employee = instance.employee
                subject = f"Update on Your Leave Request: {instance.get_status_display()}"
                message = (
                    f"Hi {employee.username},\n\n"
                    f"Your leave request from {instance.start_date} to {instance.end_date} has been {instance.get_status_display()}.\n\n"
                    f"Manager: {instance.approved_rejected_by.username}\n"
                    f"Date of Action: {instance.approved_rejected_at}"
                )
                if employee.email:
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[employee.email],
                        fail_silently=False,
                    )