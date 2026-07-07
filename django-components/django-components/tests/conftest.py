"""
Pytest configuration and global fixtures for all tests.

This module sets up the Django environment for tests and registers
Hypothesis profiles.
"""

import os

import pytest
from hypothesis import Phase, settings

# Register the failfast profile for quicker test runs during development
settings.register_profile("failfast", phases=[Phase.explicit, Phase.reuse, Phase.generate])


@pytest.fixture(scope="session", autouse=True)
def setup_django_settings():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")
    import django

    django.setup()
