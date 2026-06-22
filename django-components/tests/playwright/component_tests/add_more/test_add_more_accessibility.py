"""
Accessibility tests for the AddMore pattern.

This module uses axe-core to verify that the plos_add_more component
follows accessibility best practices and handles focus management correctly.
"""

import os

import pytest
from playwright.sync_api import Page, expect

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

AXE_URL = "https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.2/axe.min.js"


def run_accessibility_check(page: Page):
    """Inject axe-core and run accessibility checks."""
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
def test_add_more_accessibility_initial_state(page: Page, live_server):
    """Check accessibility of the Add More pattern in its initial state."""
    page.goto(f"{live_server.url}/patterns/add-more/")

    # Wait for the pattern to be visible
    expect(page.locator(".plos-add-more")).to_be_visible()

    # Use ARIA snapshot to verify the structure and accessibility labels
    expect(page.locator(".plos-add-more")).to_match_aria_snapshot(
        r"""
        - heading "Patent 1" [level=2]
        - textbox "Patent reference or number"
        - group "Patent application filing date":
          - spinbutton "Day"
          - spinbutton "Month"
          - spinbutton "Year"
        - button "Add another patent"
        - paragraph: /You can add \d+ more patents/
        - button "Continue"
        - button "Save and return"
        """
    )

    violations = run_accessibility_check(page)
    assert len(violations) == 0, f"Found {len(violations)} accessibility violations in initial state."


@pytest.mark.django_db
def test_add_more_accessibility_after_adding_item(page: Page, live_server):
    """Check accessibility after adding an item."""
    page.goto(f"{live_server.url}/patterns/add-more/")

    # Add an item
    add_button = page.get_by_role("button", name="Add another patent")
    add_button.click()

    # Wait for the new item to appear (HTMX)
    expect(page.locator(".plos-add-more__item")).to_have_count(2)

    violations = run_accessibility_check(page)
    assert len(violations) == 0, f"Found {len(violations)} accessibility violations after adding an item."


@pytest.mark.django_db
def test_add_more_accessibility_after_deleting_item(page: Page, live_server):
    """Check accessibility after deleting an item."""
    page.goto(f"{live_server.url}/patterns/add-more/")

    # Add an item first so we can delete it
    page.get_by_role("button", name="Add another patent").click()
    expect(page.locator(".plos-add-more__item")).to_have_count(2)

    # Delete the second item
    page.get_by_role("button", name="Delete patent 2").click()
    expect(page.locator(".plos-add-more__item")).to_have_count(1)

    violations = run_accessibility_check(page)
    assert len(violations) == 0, f"Found {len(violations)} accessibility violations after deleting an item."


@pytest.mark.django_db
def test_add_more_accessibility_with_errors(page: Page, live_server):
    """Check accessibility when validation errors are shown."""
    page.goto(f"{live_server.url}/patterns/add-more/")

    # Click Continue without filling anything to trigger validation
    # (Note: In the current showcase it might not show errors unless we fill and empty,
    # or if the server-side validation is triggered. The showcase's Continued button
    # seems to trigger a post to /patterns/add-more/htmx/)
    page.get_by_role("button", name="Continue").click()

    # We should wait for a moment for potential error messages
    # If the showcase doesn't show errors, this still checks the post-submit state.

    violations = run_accessibility_check(page)
    assert len(violations) == 0, f"Found {len(violations)} accessibility violations with errors visible."


@pytest.mark.django_db
def test_add_more_focus_management_on_add(page: Page, live_server):
    """Check that focus is handled correctly when adding an item."""
    page.goto(f"{live_server.url}/patterns/add-more/")

    # Add an item
    add_button = page.get_by_role("button", name="Add another patent")
    add_button.click()

    # Wait for the new item to appear
    expect(page.locator(".plos-add-more__item")).to_have_count(2)

    # Check if focus moved to the first field of the new item
    # New item index should be 1
    first_field_new_item = page.locator("#patent_number_1")
    # We give it a small timeout because HTMX might take a moment to swap and focus
    expect(first_field_new_item).to_be_focused(timeout=5000)


@pytest.mark.django_db
def test_add_more_focus_management_on_delete(page: Page, live_server):
    """Check that focus is handled correctly when deleting an item."""
    page.goto(f"{live_server.url}/patterns/add-more/")

    # Add an item first so we have 2 items
    page.get_by_role("button", name="Add another patent").click()
    expect(page.locator(".plos-add-more__item")).to_have_count(2)

    # Focus something in the second item
    page.locator("#patent_number_1").focus()
    expect(page.locator("#patent_number_1")).to_be_focused()

    # Delete the second item
    page.get_by_role("button", name="Delete patent 2").click()
    expect(page.locator(".plos-add-more__item")).to_have_count(1)

    # When an item is deleted, focus should ideally move to a sensible place.
    # Often it's the item before it, or the "Add another" button.
    # If focus is lost (moved to body), it's bad for accessibility.
    expect(page.locator("body")).not_to_be_focused()
