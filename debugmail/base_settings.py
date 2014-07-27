from django.conf import settings

SEND_TO_REAL_RECIPIENTS = getattr(settings, 'MAILER_SEND_TO_REAL_RECIPIENTS', False)
SEND_TO_TEST_RECIPIENTS = getattr(settings, 'MAILER_SEND_TO_TEST_RECIPIENTS', False)
SEND_TO_ADMINS = getattr(settings, 'MAILER_SEND_TO_ADMINS', True)
SAVE_TO_DATABASE = getattr(settings, 'MAILER_SAVE_TO_DATABASE', True)
ALSO_BCC = getattr(settings, 'MAILER_ALSO_BCC', False)
BCC_RECIPIENTS = getattr(settings, 'MAILER_BCC_RECIPIENTS', None)
TEST_RECIPIENTS = getattr(settings, 'MAILER_TEST_RECIPIENTS', None)

