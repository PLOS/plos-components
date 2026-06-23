"""
Playwright tests for the AddMore pattern with JavaScript disabled.

This module verifies that the plos_add_more component remains fully functional
without JavaScript, relying on standard form submissions.
"""

import os

import pytest
from playwright.sync_api import expect

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"


@pytest.mark.django_db
def test_add_more_non_js_autofocus(browser, live_server):
    """
    Test that autofocus works in non-JS mode when adding an item.
    """
    # Create a context with JavaScript disabled
    context = browser.new_context(java_script_enabled=False)
    page = context.new_page()

    page.goto(f"{live_server.url}/patterns/add-more/")

    # Initially 1 item
    expect(page.locator(".plos-add-more__item")).to_have_count(1)

    # Click "Add another patent" - this will be a full POST
    page.get_by_role("button", name="Add another patent").click()

    # Now 2 items
    expect(page.locator(".plos-add-more__item")).to_have_count(2)

    # The second item's first input should have autofocus
    # In HTML, the autofocus attribute should be present
    new_input = page.locator("#patent_number_1")
    expect(new_input).to_have_attribute("autofocus", "")


@pytest.mark.django_db
def test_add_more_non_js_item_deletion(browser, live_server):
    """
    Test that item deletion works in non-JS mode.
    """
    context = browser.new_context(java_script_enabled=False)
    page = context.new_page()

    page.goto(f"{live_server.url}/patterns/add-more/")

    # Add an item to have 2
    page.get_by_role("button", name="Add another patent").click()
    expect(page.locator(".plos-add-more__item")).to_have_count(2)

    # Fill some data in both
    page.locator("#patent_number_0").fill("KEEP-ME")
    page.locator("#patent_number_1").fill("DELETE-ME")

    # Delete the second item
    page.get_by_role("button", name="Delete patent 2").click()

    # Now back to 1 item
    expect(page.locator(".plos-add-more__item")).to_have_count(1)

    # Verify the correct item was kept
    expect(page.locator("#patent_number_0")).to_have_value("KEEP-ME")
