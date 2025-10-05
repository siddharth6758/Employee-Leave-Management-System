from django.core.mail import send_mail
from django.dispatch import receiver
from django.conf import settings
from django.db.models.signals import post_save
from employee.models import Delegation

@receiver(post_save, sender=Delegation)
def send_delegation_notification(sender, instance, created, **kwargs):
    if created:
        # mail for new delegation just created
        manager = instance.manager
        delegate = instance.delegate

        if delegate and delegate.email:
            subject = f"New Delegation Assigned by {manager.username}"
            message = (
                f"You have been assigned as a delegate by {manager.username}.\n\n"
                f"Delegation Period: {instance.start_date} to {instance.end_date}\n"
            )
            # send the email to the delegate if email exists
            if delegate.email:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[delegate.email],
                    fail_silently=False,
                )