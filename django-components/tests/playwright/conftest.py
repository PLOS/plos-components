import os

import pytest


@pytest.fixture(scope="session", autouse=True)
def setup_django_settings():
    os.environ["DJANGO_SETTINGS_MODULE"] = "tests.playwright.test_app.settings"
    import django

    django.setup()
