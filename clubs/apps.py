from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class ClubsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'clubs'

class HumanizeConfig(AppConfig):
    name = 'django.contrib.humanize'
    verbose_name = _("Humanize")