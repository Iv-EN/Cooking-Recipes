from django.conf import settings

HELP_EMAIL = (
    'Необходимо указать. '
    f'Максимум {settings.MAX_LEN_EMAIL_FIELD} знаков.'
)
HELP_USERNAME = (
    'Необходимо указать. '
    'Это имя будет отображаться в системе. '
    f'Максимум {settings.MAX_LEN_USERS_FIELD} знаков.'
)
HELP_FIRST_NAME = (
    'Необходимо указать. '
    f'Максимум {settings.MAX_LEN_USERS_FIELD} знаков.'
)
HELP_LAST_NAME = (
    'Необходимо указать. '
    f'Максимум {settings.MAX_LEN_USERS_FIELD} знаков.'
)
