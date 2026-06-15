import os

from plos_django_components import apps as _plos_apps

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLOS_COMPONENTS_DIR = os.path.dirname(os.path.abspath(_plos_apps.__file__))
# SHOWCASE_DIR is hardcoded because it is not installed as a package
SHOWCASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(BASE_DIR))), "design_system", "showcase")

SECRET_KEY = "playwright-test-key"
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "django_components",
    "plos_django_components",
    "showcase",
    "tests.playwright.test_app",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
]

ROOT_URLCONF = "tests.playwright.test_app.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [PLOS_COMPONENTS_DIR, os.path.join(SHOWCASE_DIR, "templates")],
        "OPTIONS": {
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
                "django_components.template_loader.Loader",
            ],
            "builtins": [
                "django_components.templatetags.component_tags",
            ],
        },
    }
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.db"
STATIC_URL = "/static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

GOV_UK_TEMPLATE_PRIMARY_CSS = "https://ux.plos.org/assets/v3/styles/gov-uk-frontend-v6.min.css"
GOV_UK_TEMPLATE_OVERRIDE_CSS = ["https://ux.plos.org/assets/v3/styles/plos-overrides.min.css"]
GOV_UK_TEMPLATE_PRIMARY_JS = "https://ux.plos.org/assets/v3/scripts/gov-uk-frontend-v6.min.js"
