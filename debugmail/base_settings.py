from django.conf import settings

SEND_TO_REAL_RECIPIENTS = getattr(settings, 'MAILER_SEND_TO_REAL_RECIPIENTS', False)
SEND_TO_TEST_RECIPIENTS = getattr(settings, 'MAILER_SEND_TO_TEST_RECIPIENTS', False)
SEND_TO_ADMINS = getattr(settings, 'MAILER_SEND_TO_ADMINS', True)
LOG_TO_DB = getattr(settings, 'MAILER_LOG_TO_DB', True)
LOG_ALL_TO_DB = getattr(settings, 'MAILER_LOG_ALL_TO_DB', False)
ALSO_BCC_REAL_EMAILS = getattr(settings, 'MAILER_ALSO_BCC_REAL_EMAILS', False)
BCC_RECIPIENTS = getattr(settings, 'MAILER_BCC_RECIPIENTS', None)
TEST_RECIPIENTS = getattr(settings, 'MAILER_TEST_RECIPIENTS', None)
TEST_RECIPIENTS_GETTER = getattr(settings, 'MAILER_TEST_RECIPIENTS_GETTER', None)
EXCLUDE_DJANGO_EMAILS = getattr(settings, 'MAILER_EXCLUDE_DJANGO_EMAILS', True)

