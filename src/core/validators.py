from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

alphanumeric = RegexValidator(
    r'^[0-9a-zA-Z]*$',
    _('Only alphanumeric characters are allowed.')
)
letters_only = RegexValidator(
    r'^[a-zA-Z ]*$',
    _('Only letters are allowed.'))
