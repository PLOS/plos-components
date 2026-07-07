"""
Pytest configuration and global fixtures for Playwright tests.

This module registers Hypothesis profiles for Playwright tests.
"""

from hypothesis import Phase, settings

settings.register_profile("failfast", phases=[Phase.explicit, Phase.reuse, Phase.generate])
