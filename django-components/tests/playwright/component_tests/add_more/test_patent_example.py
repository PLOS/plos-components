import os

import pytest
from hypothesis import HealthCheck, given
from hypothesis import settings as hypothesis_settings
from hypothesis import strategies as st
from playwright.sync_api import Page, expect

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"


@pytest.mark.django_db
def test_patent_example_loads_database_values(page: Page, live_server):
    page.goto(f"{live_server.url}/patterns/add-more/patent-example/")

    # Check if database values are loaded into the inputs
    expect(page.locator("input[name='patent_number_0']")).to_have_value("123")
    expect(page.locator("textarea[name='patent_description_0']")).to_have_value("First patent")
    expect(page.locator("input[name='patent_number_1']")).to_have_value("456")
    expect(page.locator("textarea[name='patent_description_1']")).to_have_value("Second patent")


@pytest.mark.django_db
def test_patent_example_add_and_save(page: Page, live_server):
    page.goto(f"{live_server.url}/patterns/add-more/patent-example/")

    # Add a new item
    page.get_by_role("button", name="Add another patent").click()

    # Fill the new item
    page.locator("input[name='patent_number_2']").fill("789")
    page.locator("textarea[name='patent_description_2']").fill("Third patent")

    # Save all
    page.get_by_role("button", name="Save All Patents").click()

    # Check if saved data is displayed
    expect(page.locator("#saved-data")).to_be_visible()
    expect(page.locator(".saved-item")).to_have_count(3)
    expect(page.locator(".saved-number").nth(2)).to_have_text("789")
    expect(page.locator(".saved-description").nth(2)).to_have_text("Third patent")


@pytest.mark.django_db
def test_patent_example_delete_and_save(page: Page, live_server):
    page.goto(f"{live_server.url}/patterns/add-more/patent-example/")

    # Delete the first item
    page.get_by_role("button", name="Delete patent 1").click()

    # Save all
    page.get_by_role("button", name="Save All Patents").click()

    # Check if only one item remains (the second one which is now first)
    expect(page.locator(".saved-item")).to_have_count(1)
    expect(page.locator(".saved-number")).to_have_text("456")


@pytest.mark.django_db
def test_patent_example_malformed_database_values(page: Page, live_server):
    # Load with malformed data
    page.goto(f"{live_server.url}/patterns/add-more/patent-example/?malformed=true")

    # Should see an error message in the error summary
    expect(page.locator(".govuk-error-summary")).to_be_visible()
    expect(page.locator(".govuk-error-summary__list")).to_contain_text("Invalid format for incoming values")

    # Should still show at least one empty item (min_items default is 1)
    expect(page.locator("input[name='patent_number_0']")).to_be_visible()
    expect(page.locator("input[name='patent_number_0']")).to_have_value("")


@pytest.mark.django_db
def test_patent_example_session_persistence_with_db_values(page: Page, live_server):
    page.goto(f"{live_server.url}/patterns/add-more/patent-example/")

    # Modify one value but don't save yet
    page.locator("input[name='patent_number_0']").fill("Modified 123")

    # Trigger an HTMX action (add)
    page.get_by_role("button", name="Add another patent").click()

    # Check if modifications are preserved (from session) and not overwritten by DB values on reload
    expect(page.locator("input[name='patent_number_0']")).to_have_value("Modified 123")
    expect(page.locator("input[name='patent_number_2']")).to_be_visible()


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
                    "field": st.one_of(st.just("number"), st.just("description")),
                    "value": st.text(
                        alphabet=st.characters(blacklist_categories=("Cs",), blacklist_characters="\x00"),
                        min_size=0,
                        max_size=100,
                    ),
                }
            ),
            st.fixed_dictionaries({"type": st.just("save")}),
            st.fixed_dictionaries({"type": st.just("reload")}),
        ),
        min_size=1,
        max_size=20,
    )
)
def test_patent_example_property_based(page: Page, live_server, actions):
    """
    Property-based test for the Patent Example, covering add, delete, fill, save and reload.
    """
    page.context.clear_cookies()
    page.goto(f"{live_server.url}/patterns/add-more/patent-example/")

    # Initial state from "database" in views.py
    current_items = [
        {"number": "123", "description": "First patent"},
        {"number": "456", "description": "Second patent"},
    ]
    # State saved in session
    session_items = [item.copy() for item in current_items]

    max_items = 10
    min_items = 1

    for action in actions:
        if action["type"] == "add":
            if len(current_items) < max_items:
                page.get_by_role("button", name="Add another patent").click()
                current_items.append({"number": "", "description": ""})
                # HTMX action saves current state to session
                session_items = [item.copy() for item in current_items]

        elif action["type"] == "delete":
            idx = action["index"]
            if len(current_items) > min_items and 0 <= idx < len(current_items):
                page.get_by_role("button", name=f"Delete patent {idx + 1}").click()
                current_items.pop(idx)
                # HTMX action saves current state to session
                session_items = [item.copy() for item in current_items]

        elif action["type"] == "fill":
            idx = action["index"]
            if 0 <= idx < len(current_items):
                val = action["value"]
                field_type = action["field"]
                if field_type == "number":
                    page.locator(f"input[name='patent_number_{idx}']").fill(val)
                    current_items[idx]["number"] = val
                else:
                    page.locator(f"textarea[name='patent_description_{idx}']").fill(val)
                    current_items[idx]["description"] = val
                # Session is NOT updated

        elif action["type"] == "save":
            page.get_by_role("button", name="Save All Patents").click()
            # The view logic in views.py only saves if number or description is truthy
            expected_saved = [item for item in current_items if item["number"] or item["description"]]

            # Verify saved data is displayed
            if expected_saved:
                expect(page.locator("#saved-data")).to_be_visible()
                expect(page.locator(".saved-item")).to_have_count(len(expected_saved))
                for i, item in enumerate(expected_saved):
                    expect(page.locator(".saved-number").nth(i)).to_have_text(item["number"])
                    expect(page.locator(".saved-description").nth(i)).to_have_text(item["description"])

            # After save, the form state reflects what was saved.
            # If nothing was saved, it defaults back to 1 empty item.
            if not expected_saved:
                current_items = [{"number": "", "description": ""}]
            else:
                current_items = [item.copy() for item in expected_saved]
            session_items = [item.copy() for item in current_items]

        elif action["type"] == "reload":
            page.reload()
            current_items = [item.copy() for item in session_items]

        # Check UI consistency
        items = page.locator(".plos-add-more__item")
        expect(items).to_have_count(len(current_items))
        for i, item in enumerate(current_items):
            expect(page.locator(f"input[name='patent_number_{i}']")).to_have_value(item["number"])
            expect(page.locator(f"textarea[name='patent_description_{i}']")).to_have_value(item["description"])
