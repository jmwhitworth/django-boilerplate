from allauth.account.adapter import DefaultAccountAdapter

from .tasks import send_email_async


class AsyncAccountAdapter(DefaultAccountAdapter):
    def send_mail(self, template_prefix, email, context):
        """Sends email using an asynchronous task queue."""

        # Render the email using allauth's internal logic
        # This returns a django.core.mail.EmailMessage or EmailMultiAlternatives
        msg = self.render_mail(template_prefix, email, context)

        # Extract alternatives (e.g. HTML version) if present
        alternatives = getattr(msg, "alternatives", [])

        # Enqueue the task
        send_email_async.enqueue(
            subject=msg.subject,
            body=msg.body,
            from_email=msg.from_email,
            to=msg.to,
            alternatives=alternatives,
        )
