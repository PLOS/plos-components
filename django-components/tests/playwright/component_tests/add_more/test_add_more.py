"""
Playwright tests for the plos_add_more pattern.

Run with `--liveserver localhost:3000` so GOV.UK Frontend loads from ux.plos.org (CORS).
"""

import os

import pytest
from django.urls import reverse
from playwright.sync_api import Browser, Page, expect

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"


def add_button(page: Page):
    return page.get_by_role("button", name="Add another patent")


@pytest.mark.django_db
def test_add_item_swaps_in_place(page: Page, live_server):
    page.goto(live_server.url + reverse("add_more"))
    page.evaluate("window.notReloaded = true")

    page.locator("#patent_0").fill("Patent-123")
    add_button(page).click()

    expect(page.locator("#patent_1")).to_be_focused()
    expect(page.locator("#patent_0")).to_have_value("Patent-123")
    expect(page.get_by_text("You can add 1 more patents")).to_be_visible()
    assert page.evaluate("window.notReloaded") is True


@pytest.mark.django_db
def test_delete_item_renumbers_remaining(page: Page, live_server):
    page.goto(live_server.url + reverse("add_more"))
    page.locator("#patent_0").fill("Patent-123")
    add_button(page).click()
    page.locator("#patent_1").fill("Patent-456")

    page.get_by_role("button", name="Delete patent 1").click()

    expect(page.locator("#patent_0")).to_have_value("Patent-456")
    expect(page.locator("#patent_0")).to_be_focused()
    expect(page.locator("#patent_1")).to_have_count(0)
    expect(page.get_by_role("button", name="Delete patent 1")).to_have_count(0)


@pytest.mark.django_db
def test_add_button_hidden_at_max_items(page: Page, live_server):
    page.goto(live_server.url + reverse("add_more"))
    add_button(page).click()
    expect(page.locator("#patent_1")).to_be_visible()
    add_button(page).click()

    expect(page.locator("#patent_2")).to_be_visible()
    expect(add_button(page)).to_have_count(0)


@pytest.mark.django_db
def test_save_shows_errors_then_saves(page: Page, live_server):
    page.goto(live_server.url + reverse("add_more"))
    page.locator("#patent_0").fill("Patent-123")
    add_button(page).click()

    page.get_by_role("button", name="Save").click()

    error_link = page.locator(".govuk-error-summary a")
    expect(error_link).to_have_text("Patent 2: Enter a patent number")
    expect(error_link).to_have_attribute("href", "#patent_1")

    page.locator("#patent_1").fill("Patent-456")
    page.get_by_role("button", name="Save").click()

    expect(page.locator("#saved li")).to_have_text(["Patent-123", "Patent-456"])


@pytest.mark.django_db
def test_add_and_delete_without_javascript(browser: Browser, live_server):
    context = browser.new_context(java_script_enabled=False)
    page = context.new_page()
    page.goto(live_server.url + reverse("add_more"))

    page.locator("#patent_0").fill("Patent-123")
    add_button(page).click()
    expect(page.locator("#patent_1")).to_be_visible()
    expect(page.locator("#patent_0")).to_have_value("Patent-123")

    page.get_by_role("button", name="Delete patent 1").click()
    expect(page.locator("#patent_1")).to_have_count(0)
    expect(page.locator("#patent_0")).to_have_value("")
    context.close()
