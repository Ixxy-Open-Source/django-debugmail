from django.utils.module_loading import import_string
from .base_settings import *
import logging
from django.core.mail.backends.smtp import EmailBackend


logger = logging.getLogger(__name__)

try:
    from email_logger.models import log_emails
except ImportError:
    # Simple fallback if email_logger isn't installed
    log_emails = lambda label, emails: logger.debug(label, [email for email in emails])


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

        if LOG_ALL_TO_DB:
            log_emails('to alternates', email_messages)


    def send_messages(self, email_messages):

        if SEND_TO_TEST_RECIPIENTS:

            if TEST_RECIPIENTS_GETTER is not None:
                test_recipients = import_string(TEST_RECIPIENTS_GETTER)()
            else:
                test_recipients = TEST_RECIPIENTS
            print "-"*80
            print test_recipients
            print "-"*80
            # self._send_to_alternates(
            #     email_messages,
            #     test_recipients,
            # )

        if SEND_TO_ADMINS:
            self._send_to_alternates(
                email_messages=email_messages,
                alternates=[admin[1] for admin in settings.ADMINS]
            )

        if SEND_TO_REAL_RECIPIENTS:

            if ALSO_BCC_REAL_EMAILS:
                for email in email_messages:
                    email.bcc += BCC_RECIPIENTS

            count = super(DebugEmailBackend, self).send_messages(email_messages)

            if LOG_TO_DB:
                log_emails('to real', email_messages)

            return count


