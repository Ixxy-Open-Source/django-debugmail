from .base_settings import *
import copy
import logging
from django.core.mail.backends.smtp import EmailBackend
try:
    from django.utils.module_loading import import_string
except ImportError: # django version older than 1.7
    from django.utils.module_loading import import_by_path as import_string

logger = logging.getLogger(__name__)

try:
    from email_logger.models import log_emails
except ImportError:
    # Simple fallback if email_logger isn't installed
    log_emails = lambda label, emails: logger.debug(label, [email for email in emails])


class DebugEmailBackend(EmailBackend):

    # Note - we catch exceptions whenever we can.
    # Yes - it's bad to catch exceptions broadly
    # but not as bad as failing to send emails to customers

    def _send_to_alternates(self, email_messages, alternates):
        
        """
        Sends emails to testers, admins etc. with a modified subject line
        indicating who the original recipients were set as
        """
        
        email_messages = [copy.copy(email) for email in email_messages]
        
        for email in email_messages:
            try:
                email.subject = u"{0} [To: {1} Cc: {2} Bcc: {3}]".format(
                    email.subject,
                    u', '.join(email.to),
                    u', '.join(email.cc),
                    u', '.join(email.bcc)
                )
            except Exception:
                email.subject = "[Error constructing email subject]"
                
            email.to = alternates
            email.cc = []
            email.bcc = []

        super(DebugEmailBackend, self).send_messages(email_messages)

        if LOG_ALL_TO_DB:
            log_emails('to alternates', email_messages)

    def send_messages(self, email_messages):
        
        # Get these each time as potentially the getter could use a database field
        # or similar dynamic source
        
        try:
            if TEST_RECIPIENTS_GETTER is not None:
                test_recipients = import_string(TEST_RECIPIENTS_GETTER)()
            else:
                test_recipients = TEST_RECIPIENTS
        except Exception:
            logger.error("Failed to get test_recipients")
            test_recipients = []
            
        try:
            if BCC_RECIPIENTS_GETTER is not None:
                bcc_recipients = import_string(BCC_RECIPIENTS_GETTER)()
            else:
                bcc_recipients = BCC_RECIPIENTS
        except Exception:
            logger.error("Failed to get bcc list")
            bcc_recipients = []
            
        try:
            admins = [admin[1] for admin in settings.ADMINS]
        except Exception:
            logger.error("Failed to get admin recipients")
            admins = []
        
        # Send to admin and test recipients
        
        try:
            alternates = []
            if SEND_TO_TEST_RECIPIENTS:
                alternates += test_recipients
            if SEND_TO_ADMINS:
                alternates += admins
            if alternates:
                self._send_to_alternates(
                    email_messages=email_messages,
                    alternates=alternates,
                )
        except Exception:
            logger.error("Failed to send test emails")
                
        except Exception:
            # It's bad to catch exceptions broadly
            # but not as bad as failing to send emails to customers
            logger.error("Failed to send test emails")
            
        # Send to real recipients and bcc if requested

        if SEND_TO_REAL_RECIPIENTS:

            try:
                if bcc_recipients:
                    for email in email_messages:
                        email.bcc += bcc_recipients
            except Exception:
                logger.error("Failed to set bcc on real emails")

            count = super(DebugEmailBackend, self).send_messages(email_messages)
            
            try:
                if LOG_TO_DB:
                    if EXCLUDE_DJANGO_EMAILS:
                        email_messages = filter(lambda x: not x.subject.startswith('[Django]'), email_messages)
                    log_emails('to real', email_messages)
            except Exception:
                logger.error("Failed to log emails")

            return count


