"""
Views for testing the Icon component in the Playwright test application.
"""

from django.shortcuts import render


def icon_showcase_view(request):
    return render(request, "playwright_test_app/icon/icon_showcase.html")
