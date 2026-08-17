from django.core.mail import EmailMultiAlternatives
from django_tasks import task


@task()
def send_email_async(subject, body, from_email, to, alternatives=None):
    """Task to send email asynchronously via the configured Django EMAIL_BACKEND."""
    msg = EmailMultiAlternatives(
        subject=subject, body=body, from_email=from_email, to=to
    )

    if alternatives:
        for content, mimetype in alternatives:
            msg.attach_alternative(content, mimetype)
    msg.send()
