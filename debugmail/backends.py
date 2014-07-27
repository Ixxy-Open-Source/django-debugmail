from .base_settings import *
from django.core.mail.backends.smtp import EmailBackend
from email_logger.models import log_emails

class DebugEmailBackend(EmailBackend):

    def _send_to_alternates(self, email_messages, alternates):

        for email in email_messages:

            email.subject = u"{0} [To: {1} Cc: {2} Bcc: {3}]".format(
                email.subject,
                u', '.join(email.to),
                u', '.join(email.cc),
                u', '.join(email.bcc)
            )
            email.to = alternates
            email.cc = []
            email.bcc = []

        super(DebugEmailBackend, self).send_messages(email_messages)

    def send_messages(self, email_messages):

        if SEND_TO_TEST_RECIPIENTS:
            self._send_to_alternates(
                email_messages,
                TEST_RECIPIENTS,
            )

        if SEND_TO_ADMINS:
            self._send_to_alternates(
                email_messages=email_messages,
                alternates=[admin[1] for admin in settings.ADMINS]
            )

        if SEND_TO_REAL_RECIPIENTS:

            if ALSO_BCC:
                for email in email_messages:
                    email.bcc += BCC_RECIPIENTS

            count = super(DebugEmailBackend, self).send_messages(email_messages)

            if SAVE_TO_DATABASE:
                log_emails(email_messages)

            return count


