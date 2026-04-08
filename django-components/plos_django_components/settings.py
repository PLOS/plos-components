import os

INSTALLED_APPS = [
    "django_components",
    "plos_django_components",
]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(BASE_DIR)))

TEMPLATES = [
    {
        "OPTIONS": {
            "loaders": (
                "django.template.loaders.cached.Loader",
                [
                    "django.template.loaders.filesystem.Loader",
                    "django.template.loaders.app_directories.Loader",
                    "django_components.template_loader.Loader",
                ],
            ),
            "builtins": [
                "django_components.templatetags.component_tags",
            ],
        },
    }
]

GOV_UK_TEMPLATE_PRIMARY_CSS = (
    "https://YOUR_SOURCE_OR_CDN_URI/stylesheets/govuk-frontend-<VERSION-NUMBER>.min.css"
)
GOV_UK_TEMPLATE_OVERRIDE_CSS = [
    "https://YOUR_SOURCE_OR_CDN_URI/stylesheets/override-<VERSION-NUMBER>.min.css"
]
GOV_UK_TEMPLATE_PRIMARY_JS = "https://YOUR_SOURCE_OR_CDN_URI/assets/v3/scripts/gov-uk-frontend-<VERSION-NUMBER>.min.js"
