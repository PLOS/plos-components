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
            )
        }
    }
]
