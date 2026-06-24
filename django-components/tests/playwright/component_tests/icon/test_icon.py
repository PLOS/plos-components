"""
Playwright tests for the Icon component.

This module tests the icon component's rendering and accessibility features.
"""

import os
import re

import pytest
from django.urls import reverse
from playwright.sync_api import Page, expect

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

AXE_URL = "https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.2/axe.min.js"


def run_accessibility_check(page: Page):
    """
    Inject axe-core and run accessibility checks on the current page.

    This function loads the axe-core accessibility testing library and runs it
    against the current page, reporting any accessibility violations found.

    Args:
        page (Page): The Playwright page object to test.

    Returns:
        list: A list of accessibility violations found by axe-core.
    """
    # Ensure axe-core is loaded
    page.add_script_tag(url=AXE_URL)

    # Run axe
    results = page.evaluate("axe.run()")

    violations = results.get("violations", [])
    if violations:
        print(f"\nFound {len(violations)} accessibility violations:")
        for i, violation in enumerate(violations, 1):
            print(f"{i}. {violation['id']}: {violation['help']}")
            print(f"   Impact: {violation['impact']}")
            print(f"   Nodes: {len(violation['nodes'])}")
            for node in violation["nodes"]:
                print(f"     - Selector: {node['target']}")
                print(f"       HTML: {node['html']}")

    return violations


@pytest.mark.django_db
def test_icon_basic_rendering(page: Page, live_server):
    """
    Test that basic icons render correctly.

    This test verifies that the icon component renders the expected HTML elements
    with the correct CSS classes for preset icons.

    Args:
        page (Page): The Playwright page object.
        live_server: The Django live server fixture.
    """
    url = live_server.url + reverse("icon_showcase")
    page.goto(url)

    # Check that icons are present
    icons = page.locator(".plos-icon")
    expect(icons).to_have_count(12)  # Total number of icons in the showcase

    # Check specific icons
    check_circle = page.locator(".plos-icon >> i.bi-check-circle-fill")
    expect(check_circle).to_be_visible()

    exclamation_circle = page.locator(".plos-icon >> i.bi-exclamation-circle-fill")
    expect(exclamation_circle).to_be_visible()

    info_circle = page.locator(".plos-icon >> i.bi-info-circle-fill")
    expect(info_circle).to_be_visible()


@pytest.mark.django_db
def test_icon_sizes(page: Page, live_server):
    """
    Test that icons render with different sizes.

    This test verifies that icons render correctly with all supported size options
    (xs, sm, md, lg, xl) and that the appropriate inline styles are applied.

    Args:
        page (Page): The Playwright page object.
        live_server: The Django live server fixture.
    """
    url = live_server.url + reverse("icon_showcase")
    page.goto(url)

    # Check different sizes
    xs_icon = page.locator(".plos-icon >> i.bi-plus-lg").first
    expect(xs_icon).to_be_visible()
    # Check the style attribute for size
    expect(xs_icon.locator("..")).to_have_attribute("style", "width: 16px; height: 16px;")

    sm_icon = page.locator(".plos-icon >> i.bi-plus-lg").nth(1)
    expect(sm_icon).to_be_visible()
    expect(sm_icon.locator("..")).to_have_attribute("style", "width: 20px; height: 20px;")

    md_icon = page.locator(".plos-icon >> i.bi-plus-lg").nth(2)
    expect(md_icon).to_be_visible()
    expect(md_icon.locator("..")).to_have_attribute("style", "width: 24px; height: 24px;")

    lg_icon = page.locator(".plos-icon >> i.bi-plus-lg").nth(3)
    expect(lg_icon).to_be_visible()
    expect(lg_icon.locator("..")).to_have_attribute("style", "width: 32px; height: 32px;")

    xl_icon = page.locator(".plos-icon >> i.bi-plus-lg").nth(4)
    expect(xl_icon).to_be_visible()
    expect(xl_icon.locator("..")).to_have_attribute("style", "width: 40px; height: 40px;")


@pytest.mark.django_db
def test_icon_display_options(page: Page, live_server):
    """
    Test that icons render with different display options.

    This test verifies that icons render correctly with both inline and block
    display modes, applying the appropriate CSS classes.

    Args:
        page (Page): The Playwright page object.
        live_server: The Django live server fixture.
    """
    url = live_server.url + reverse("icon_showcase")
    page.goto(url)

    # Check inline display
    inline_icon = page.locator("p:has-text('Inline icon') >> .plos-icon--inline")
    expect(inline_icon).to_be_visible()

    # Check block display
    block_icon = page.locator("div:has(> p:has-text('Block icon')) >> .plos-icon--block")
    expect(block_icon).to_be_visible()


@pytest.mark.django_db
def test_icon_custom_icon(page: Page, live_server):
    """
    Test that custom icons render correctly.

    This test verifies that custom icon classes can be used with the icon component
    and that they render with the correct CSS classes.

    Args:
        page (Page): The Playwright page object.
        live_server: The Django live server fixture.
    """
    url = live_server.url + reverse("icon_showcase")
    page.goto(url)

    # Check custom icon
    custom_icon = page.locator(".plos-icon >> i.bi-heart-fill")
    expect(custom_icon).to_be_visible()


@pytest.mark.django_db
def test_icon_with_field_id(page: Page, live_server):
    """
    Test that icons render with field IDs.

    This test verifies that custom IDs can be applied to icon elements and
    that they are correctly set in the rendered HTML.

    Args:
        page (Page): The Playwright page object.
        live_server: The Django live server fixture.
    """
    url = live_server.url + reverse("icon_showcase")
    page.goto(url)

    # Check icon with field ID
    icon_with_id = page.locator("#delete-icon-1")
    expect(icon_with_id).to_be_visible()
    expect(icon_with_id).to_have_class(re.compile(r"plos-icon"))


@pytest.mark.django_db
def test_icon_accessibility(page: Page, live_server):
    """
    Test that icons are accessible.

    This test runs the axe-core accessibility checker to verify that icon
    components meet accessibility standards.

    Args:
        page (Page): The Playwright page object.
        live_server: The Django live server fixture.
    """
    url = live_server.url + reverse("icon_showcase")
    page.goto(url)

    # Run accessibility check
    violations = run_accessibility_check(page)
    assert len(violations) == 0, f"Found {len(violations)} accessibility violations."


@pytest.mark.django_db
def test_icon_aria_hidden(page: Page, live_server):
    """
    Test that icons have aria-hidden attribute.

    This test verifies that all icons are rendered with the aria-hidden="true"
    attribute, making them decorative for accessibility purposes.

    Args:
        page (Page): The Playwright page object.
        live_server: The Django live server fixture.
    """
    url = live_server.url + reverse("icon_showcase")
    page.goto(url)

    # Check that icons have aria-hidden="true"
    icons = page.locator(".plos-icon >> i")
    count = icons.count()

    for i in range(count):
        icon = icons.nth(i)
        expect(icon).to_have_attribute("aria-hidden", "true")
