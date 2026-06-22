"""
Pytest configuration and global fixtures for Playwright tests.

This module sets up the Django environment for Playwright tests and registers
Hypothesis profiles.
"""

import os

import pytest
from hypothesis import Phase, settings

settings.register_profile("failfast", phases=[Phase.explicit, Phase.reuse, Phase.generate])


@pytest.fixture(scope="session", autouse=True)
def setup_django_settings():
    os.environ["DJANGO_SETTINGS_MODULE"] = "tests.playwright.test_app.settings"
    import django

    django.setup()
