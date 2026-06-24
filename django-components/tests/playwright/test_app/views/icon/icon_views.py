"""
Views for testing the Icon component in the Playwright test application.
"""

from django.shortcuts import render


def icon_showcase_view(request):
    """
    Render the icon showcase page for Playwright tests.

    This view renders a page that displays various icon components with different
    configurations for testing purposes.

    Args:
        request: The Django HTTP request object.

    Returns:
        HttpResponse: The rendered icon showcase page.
    """
    return render(request, "playwright_test_app/icon/icon_showcase.html")
