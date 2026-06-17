"""
An application which provides a number of components in alignment with
[GovUK](https://design-system.service.gov.uk/) components.
"""

from django.apps import AppConfig


class PlosDjangoComponentsConfig(AppConfig):
    """
    The configuration for the components.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "plos_django_components"
    verbose_name = "PLOS Django Components"
