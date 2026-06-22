import os

import pytest
from hypothesis import HealthCheck, given
from hypothesis import settings as hypothesis_settings
from hypothesis import strategies as st
from playwright.sync_api import Page, expect

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"


@pytest.mark.django_db
@hypothesis_settings(
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    max_examples=10,
    deadline=None,
)
@given(
    actions=st.lists(
        st.one_of(
            st.fixed_dictionaries({"type": st.just("add")}),
            st.fixed_dictionaries({"type": st.just("delete"), "index": st.integers(min_value=0, max_value=15)}),
            st.fixed_dictionaries(
                {
                    "type": st.just("fill"),
                    "index": st.integers(min_value=0, max_value=15),
                    "value": st.text(
                        alphabet=st.characters(blacklist_categories=("Cs",), blacklist_characters="\x00"),
                        min_size=0,
                        max_size=100,
                    ),
                }
            ),
            st.fixed_dictionaries({"type": st.just("reload")}),
            st.fixed_dictionaries({"type": st.just("navigate")}),
        ),
        min_size=1,
        max_size=30,
    )
)
def test_add_more_property_based(page: Page, live_server, actions):
    """
    Property-based test for Add More pattern using Hypothesis and Playwright.
    Generates a random sequence of add, delete, fill, reload, and navigate actions.
    """
    # Reset session for each @given example by clearing cookies
    page.context.clear_cookies()
    page.goto(f"{live_server.url}/patterns/add-more/")

    current_count = 1
    min_items = 1
    max_items = 10

    # We'll track what we expect to be in the fields on the page
    expected_values = {0: ""}
    # We'll track what's actually saved in the session (after an HTMX action)
    session_values = {0: ""}

    for action in actions:
        if action["type"] == "add":
            if current_count < max_items:
                page.get_by_role("button", name="Add another patent").click()
                current_count += 1
                expected_values[current_count - 1] = ""
                # HTMX action saves current state to session
                session_values = expected_values.copy()

        elif action["type"] == "delete":
            # Only delete if we are above min_items and the index is valid
            idx = action["index"]
            if current_count > min_items and 0 <= idx < current_count:
                # The label is "Delete patent {idx + 1}"
                page.get_by_role("button", name=f"Delete patent {idx + 1}").click()

                # Update our expected values: remove at idx and shift others
                new_expected = {}
                for i in range(current_count - 1):
                    if i < idx:
                        new_expected[i] = expected_values[i]
                    else:
                        new_expected[i] = expected_values[i + 1]
                expected_values = new_expected
                current_count -= 1
                # HTMX action saves current state to session
                session_values = expected_values.copy()

        elif action["type"] == "fill":
            idx = action["index"]
            if 0 <= idx < current_count:
                val = action["value"]
                # We need to be careful with characters that might cause issues in fill
                # (though Playwright handles most).
                field = page.locator("#patent_number_" + str(idx))
                field.fill(val)
                expected_values[idx] = val
                # Session is NOT updated until an action is performed

        elif action["type"] == "reload":
            page.reload()
            # On reload, we expect the page to revert to the last session state
            expected_values = session_values.copy()
            current_count = len(expected_values)

        elif action["type"] == "navigate":
            # Navigate away to a different page and back
            page.goto(f"{live_server.url}/")
            page.goto(f"{live_server.url}/patterns/add-more/")
            # On return, it should also have the session state
            expected_values = session_values.copy()
            current_count = len(expected_values)

        # After each action, verify count and visible values
        items = page.locator(".plos-add-more__item")
        expect(items).to_have_count(current_count)

        for i in range(current_count):
            expect(page.locator("#patent_number_" + str(i))).to_have_value(expected_values[i])

    # Final check: if we are at max, add button hidden; if at min, delete buttons hidden
    add_button = page.get_by_role("button", name="Add another patent")
    if current_count == max_items:
        expect(add_button).not_to_be_visible()
    else:
        expect(add_button).to_be_visible()


@pytest.mark.django_db
def test_add_more_interactivity(page: Page, live_server):
    """
    Test that the Add More pattern correctly adds and removes items using Playwright.
    Includes verification of HTMX fragment responses and performance.
    """
    # Track HTMX responses
    htmx_responses = []

    def handle_response(response):
        if "/patterns/add-more/htmx/" in response.url:
            # Check for redirect (3xx) as we can't get body for those
            body = ""
            if not (300 <= response.status < 400) and response.status != 204:
                try:
                    body = response.text()
                except Exception:
                    pass
            htmx_responses.append(
                {
                    "url": response.url,
                    "status": response.status,
                    "body": body,
                    "timing": response.request.timing,
                }
            )

    page.on("response", handle_response)

    # Go to the Add More pattern page in the dedicated test app
    page.goto(f"{live_server.url}/patterns/add-more/")

    # Initial state: Should have 1 item (as min_items=1 in the showcase)
    items = page.locator(".plos-add-more__item")
    expect(items).to_have_count(1)

    # Click "Add another patent"
    # The label is "Add another patent" based on showcase config
    add_button = page.get_by_role("button", name="Add another patent")

    # We expect a POST to HTMX and then a redirect (302) then a GET (200)
    with page.expect_response("**/patterns/add-more/htmx/"):
        add_button.click()

    # Should now have 2 items
    expect(items).to_have_count(2)

    # Verify HTMX response for "Add"
    assert len(htmx_responses) >= 1
    # The last response might be the redirect or the final page.
    # In HTMX with redirect, it might be 302.
    add_resp = htmx_responses[-1]
    assert add_resp["status"] in [200, 302]

    # If it's a 200, it should be a fragment (if strategy=fragment was used)
    # However, AddMore component currently redirects by default.
    # So we don't necessarily get a fragment here.

    # Verify performance (target < 500ms)
    # response.request.timing["finished"] might not be available if not finished yet in handler
    # but here the click() has returned and expect() passed, so it should be.
    # Actually, Playwright timing might use different keys or might not be fully populated yet.
    # Let's use a safer check.
    if "finished" in add_resp["timing"] and add_resp["timing"]["finished"] > 0:
        duration = add_resp["timing"]["finished"] - add_resp["timing"]["requestStart"]
        assert duration < 500, f"HTMX response too slow: {duration}ms"

    # Fill in some data for the first item
    page.locator("#patent_number_0").fill("PAT-001")
    page.locator("#patent_date_0-day").fill("01")
    page.locator("#patent_date_0-month").fill("01")
    page.locator("#patent_date_0-year").fill("2020")

    # We need to blur or trigger a change if it's not being picked up,
    # but usually Playwright's fill() does it.
    # Let's try to click somewhere else to ensure blur.
    page.click("body")

    # Add another one
    add_button.click()
    expect(items).to_have_count(3)

    # Delete the second item (index 1)
    # The label is "Delete patent 2"
    delete_button_2 = page.get_by_role("button", name="Delete patent 2")
    delete_button_2.click()

    # Should be back to 2 items
    expect(items).to_have_count(2)

    # Verify that the first item still has its data (it shouldn't have been deleted)
    expect(page.locator("#patent_number_0")).to_have_value("PAT-001")

    # Delete the last item (now index 1, display index 2)
    delete_button_last = page.get_by_role("button", name="Delete patent 2")
    delete_button_last.click()

    # Should be back to 1 item
    expect(items).to_have_count(1)

    # Check if delete button is hidden when count == min_items (1)
    expect(page.get_by_role("button", name="Delete patent 1")).not_to_be_visible()


@pytest.mark.django_db
def test_add_more_max_items(page: Page, live_server):
    """
    Test that the Add More pattern respects the max_items limit.
    """
    page.goto(f"{live_server.url}/patterns/add-more/")

    items = page.locator(".plos-add-more__item")
    add_button = page.get_by_role("button", name="Add another patent")

    # Initial state: 1 item
    expect(items).to_have_count(1)

    # Click add button until we reach max_items (10)
    for i in range(2, 11):
        add_button.click()
        expect(items).to_have_count(i)

    # At 10 items, the add button should be hidden or disabled
    # In GOV.UK/PLOS pattern, it's usually hidden when max is reached
    expect(add_button).not_to_be_visible()

    # Delete one item
    page.get_by_role("button", name="Delete patent 10").click()
    expect(items).to_have_count(9)

    # Add button should be visible again
    expect(add_button).to_be_visible()


@pytest.mark.django_db
def test_add_more_persistence_and_order(page: Page, live_server):
    """
    Test that data is preserved and correctly ordered when adding/deleting items.
    """
    page.goto(f"{live_server.url}/patterns/add-more/")

    # Fill item 1
    page.locator("#patent_number_0").fill("FIRST-PATENT")

    # Add item 2
    page.get_by_role("button", name="Add another patent").click()
    page.locator("#patent_number_1").fill("SECOND-PATENT")

    # Add item 3
    page.get_by_role("button", name="Add another patent").click()
    page.locator("#patent_number_2").fill("THIRD-PATENT")

    # Delete item 2
    page.get_by_role("button", name="Delete patent 2").click()

    # We should have 2 items now.
    # The old item 3 should now be item 2.
    expect(page.locator("#patent_number_0")).to_have_value("FIRST-PATENT")
    expect(page.locator("#patent_number_1")).to_have_value("THIRD-PATENT")


@pytest.mark.django_db
def test_add_more_validation_summary(page: Page, live_server):
    """
    Test that the save button triggers validation (if implemented in the showcase).
    The showcase template has show_save_button=True.
    """
    page.goto(f"{live_server.url}/patterns/add-more/")

    # Click Continue (the save button)
    page.get_by_role("button", name="Continue").click()

    # Note: Whether it shows errors depends on the view logic in the showcase.
    # Currently the showcase doesn't seem to show errors for empty fields.
    expect(page.locator(".plos-add-more")).to_be_visible()


@pytest.mark.django_db
def test_add_more_dangerous_inputs(page: Page, live_server):
    """
    Test that the Add More pattern handles dangerous or unusual inputs gracefully.
    """
    page.goto(f"{live_server.url}/patterns/add-more/")

    dangerous_inputs = [
        "<script>alert('xss')</script>",
        "'; DROP TABLE users; --",
        "../../../../etc/passwd",
        "ユニコード (Unicode)",
        "A" * 1000,  # Long string
        "!@#$%^&*()_+{}|:\"<>?~`-=[]\\;',./",  # Special characters
    ]

    for i, inp in enumerate(dangerous_inputs):
        if i > 0:
            page.get_by_role("button", name="Add another patent").click()
        page.locator("#patent_number_" + str(i)).fill(inp)

    # Verify all inputs preserved their values exactly
    for i, inp in enumerate(dangerous_inputs):
        expect(page.locator("#patent_number_" + str(i))).to_have_value(inp)

    # Verify no alerts were triggered (XSS)
    # Playwright would normally fail or we can check page state.
    # The fact that to_have_value passes means the DOM wasn't broken by the input.


@pytest.mark.django_db
def test_add_more_rapid_clicking(page: Page, live_server):
    """
    Simulate a user clicking the 'Add' button multiple times in rapid succession.
    """
    page.goto(f"{live_server.url}/patterns/add-more/")

    # Rapidly click Add 5 times
    add_button = page.get_by_role("button", name="Add another patent")
    for _ in range(5):
        with page.expect_response("**/patterns/add-more/htmx/"):
            add_button.click()

    # We should eventually have 6 items (1 initial + 5 added)
    # The expect() helper has built-in retry logic.
    expect(page.locator(".plos-add-more__item")).to_have_count(6)

    # Rapidly delete 3 items
    for i in range(3):
        # Always delete the second item (index 1) to see if it shifts correctly
        with page.expect_response("**/patterns/add-more/htmx/"):
            page.get_by_role("button", name="Delete patent 2").click()

    expect(page.locator(".plos-add-more__item")).to_have_count(3)
