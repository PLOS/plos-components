"""
Django settings for the core django-components tests.
"""
import os

from plos_django_components.components.components.base.icon_fonts.abstract_icon_font_defaults import IconFontDictionary

SECRET_KEY = "fake-key"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_URLCONF = "tests.urls"

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django_components",
    "plos_django_components",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "OPTIONS": {
            "loaders": [
                (
                    "django.template.loaders.cached.Loader",
                    [
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                        "django_components.template_loader.Loader",
                    ],
                ),
            ],
            "builtins": [
                "django_components.templatetags.component_tags",
            ],
        },
    }
]

ICON_FONT = "bootstrap"

ICON_FONT_OVERRIDE_DICTIONARY: IconFontDictionary = dict(
    icon_font_url=None,
    icon_font_integrity=None,
)

GOV_UK_TEMPLATE_PRIMARY_CSS = "https://YOUR_SOURCE_OR_CDN_URI/stylesheets/govuk-frontend-<VERSION-NUMBER>.min.css"
GOV_UK_TEMPLATE_OVERRIDE_CSS = ["https://YOUR_SOURCE_OR_CDN_URI/stylesheets/override-<VERSION-NUMBER>.min.css"]
GOV_UK_TEMPLATE_PRIMARY_JS = "https://YOUR_SOURCE_OR_CDN_URI/assets/v3/scripts/gov-uk-frontend-<VERSION-NUMBER>.min.js"
