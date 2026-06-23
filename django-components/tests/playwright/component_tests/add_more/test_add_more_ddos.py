"""
Tests simulating DDOS-like attacks or resource exhaustion attempts on the AddMore pattern.
"""

import os

import pytest
import requests
from playwright.sync_api import Page, expect

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

@pytest.mark.django_db
def test_add_more_limit_bypass_attempt(page: Page, live_server):
    """
    Attempt to bypass max_items by manually triggering POST requests.
    The component uses a signed config, so this should fail if we try to change count/max_items
    without a valid signature.
    """
    page.goto(f"{live_server.url}/patterns/add-more/")

    # Get the signed config from the page
    config_input = page.locator('input[name="patents__config"]')
    signed_config = config_input.get_attribute("value")
    csrf_token = page.locator('input[name="csrfmiddlewaretoken"]').get_attribute("value")

    # The default max_items in the showcase is 10.
    # Let's try to send an 'add' action even when we've theoretically reached max,
    # OR try to send a 'count' that is very large in a custom POST.

    # Fill it up using Playwright
    add_button = page.get_by_role("button", name="Add another patent")
    for _ in range(9):
        add_button.click()

    expect(page.locator(".plos-add-more__item")).to_have_count(10)
    expect(add_button).not_to_be_visible()

    # Now attempt to manually POST an 'add' action using the same signed config
    # that we got when count was 1.
    # This simulates a user trying to replay an old config to bypass the limit.
    # We use page.evaluate to perform the POST from within the same browser session.

    page.evaluate(f"""
        fetch('{live_server.url}/patterns/add-more/htmx/', {{
            method: 'POST',
            headers: {{
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': '{csrf_token}',
            }},
            body: new URLSearchParams({{
                'patents__action': 'add',
                'patents__config': '{signed_config}',
            }})
        }})
    """)

    # Wait a bit for the request to complete
    page.wait_for_timeout(1000)

    # Reload and verify count is STILL 10 (or at least didn't increase based on the old config)
    page.reload()
    # If the old config (count=1) was used, the server would have set session[values] = [{}, {}]
    # which would actually REDUCE the count if it was at 10.
    # Either way, it shouldn't be more than 10.
    count = page.locator(".plos-add-more__item").count()
    assert count <= 10

@pytest.mark.django_db
def test_add_more_massive_post_body(page: Page, live_server):
    """
    Send a POST request with many fields to test how the server handles it.
    Django has DATA_UPLOAD_MAX_NUMBER_FIELDS which defaults to 1000.
    """
    page.goto(f"{live_server.url}/patterns/add-more/")

    signed_config = page.locator('input[name="patents__config"]').get_attribute("value")
    csrf_token = page.locator('input[name="csrfmiddlewaretoken"]').get_attribute("value")

    # Create a large payload, but just below or at the limit to see if it's processed correctly
    # Or purposefully go over to see if it's gracefully rejected with 400 (which it is).
    payload = {
        "patents__action": "add",
        "patents__config": signed_config,
        "csrfmiddlewaretoken": csrf_token,
    }
    for i in range(1200): # Default Django limit is 1000
        payload[f"field_{i}"] = "value"

    cookies = {c['name']: c['value'] for c in page.context.cookies()}
    response = requests.post(
        f"{live_server.url}/patterns/add-more/htmx/",
        data=payload,
        cookies=cookies,
        headers={"Referer": f"{live_server.url}/patterns/add-more/"}
    )

    # Django returns 400 when TooManyFieldsSent is raised
    assert response.status_code == 400

@pytest.mark.django_db
def test_add_more_rapid_fire_requests(page: Page, live_server):
    """
    Simulate many rapid concurrent requests to the HTMX endpoint.
    """
    page.goto(f"{live_server.url}/patterns/add-more/")

    signed_config = page.locator('input[name="patents__config"]').get_attribute("value")
    csrf_token = page.locator('input[name="csrfmiddlewaretoken"]').get_attribute("value")
    cookies = {c['name']: c['value'] for c in page.context.cookies()}

    # Use a session to keep cookies (especially sessionid)
    session = requests.Session()
    for k, v in cookies.items():
        session.cookies.set(k, v)

    # Send multiple rapid requests
    responses = []
    for _ in range(5):
        resp = session.post(
            f"{live_server.url}/patterns/add-more/htmx/",
            data={
                "patents__action": "add",
                "patents__config": signed_config,
                "csrfmiddlewaretoken": csrf_token,
            },
            headers={"Referer": f"{live_server.url}/patterns/add-more/"}
        )
        responses.append(resp)

    for resp in responses:
        assert resp.status_code in [200, 302]

    page.reload()
    # We expect at least one item to be there (the initial one)
    expect(page.locator(".plos-add-more__item").first).to_be_visible()
