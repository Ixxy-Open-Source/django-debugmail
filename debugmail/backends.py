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

        count = self.do_send_messages(email_messages, log_emails_label=LOG_ALL_TO_DB and 'to alternates')
        return count

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

            count = self.do_send_messages(email_messages, log_emails_label=LOG_TO_DB and 'to real')
            return count


    def do_send_messages(self, email_messages, log_emails_label=None):
        """
        Sends one or more EmailMessage objects and returns the number of email
        messages sent.
        When log_emails_label is set, we log the emails using email_logger
        """
        if not email_messages:
            return
        with self._lock:
            new_conn_created = self.open()
            if not self.connection:
                # We failed silently on open().
                # Trying to send would be pointless.
                return
            num_sent = 0
            for message in email_messages:
                if log_emails_label:
                    email_log = log_emails(log_emails_label, [message])[0]
                    try:
                        sent = self._send(message)
                        if sent:
                            num_sent += 1
                    except Exception, e:
                        email_log.success = False
                        email_log.save()
                        logger.error(e, exc_info=1, extra={'stack': True})
                        raise e
                else:
                    sent = self._send(message)
                    if sent:
                        num_sent += 1
            if new_conn_created:
                self.close()
        return num_sent
