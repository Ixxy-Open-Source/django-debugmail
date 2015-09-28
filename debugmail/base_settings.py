from django.conf import settings

from django.core.exceptions import ImproperlyConfigured

# Check for legacy settings and fail fast
if getattr(settings, 'MAILER_ALSO_BCC_REAL_EMAILS', False):
    raise ImproperlyConfigured(
        'MAILER_ALSO_BCC_REAL_EMAILS setting is deprecated. Instead use an empty bcc list'
    )

# Booleans for which groups to send to
SEND_TO_REAL_RECIPIENTS = getattr(settings, 'MAILER_SEND_TO_REAL_RECIPIENTS', False)
SEND_TO_TEST_RECIPIENTS = getattr(settings, 'MAILER_SEND_TO_TEST_RECIPIENTS', False)
SEND_TO_ADMINS = getattr(settings, 'MAILER_SEND_TO_ADMINS', True)

# Recipient lists
BCC_RECIPIENTS = getattr(settings, 'MAILER_BCC_RECIPIENTS', None)
TEST_RECIPIENTS = getattr(settings, 'MAILER_TEST_RECIPIENTS', None)

# Allows custom callables for getting the these recipient lists
TEST_RECIPIENTS_GETTER = getattr(settings, 'MAILER_TEST_RECIPIENTS_GETTER', None)
BCC_RECIPIENTS_GETTER = getattr(settings, 'MAILER_BCC_RECIPIENTS_GETTER', None)

# Logging

# Uses ixxy-email-logger if installed. Falls back to logger.debug otherwise
# 'LOG_TO_DB' sets whether we log sent emails at all. A single copy is logged for each email sent
# 'LOG_ALL_TO_DB' logs separately a copy for each and every recipient
LOG_TO_DB = getattr(settings, 'MAILER_LOG_TO_DB', True)
LOG_ALL_TO_DB = getattr(settings, 'MAILER_LOG_ALL_TO_DB', False)

# Should we also log Django's 404 and 500 emails?
EXCLUDE_DJANGO_EMAILS = getattr(settings, 'MAILER_EXCLUDE_DJANGO_EMAILS', True)

