import re
import string

import pytest
from django.urls import reverse
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from playwright.sync_api import Page, expect

# Use a reasonably small number of examples for Playwright tests to avoid excessive runtimes
HYPOTHESIS_SETTINGS = settings(
    max_examples=3, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture]
)

# Define a safe alphabet for E2E tests to avoid browser/encoding issues
SAFE_ALPHABET = string.ascii_letters + string.digits + " "


@pytest.mark.django_db
@given(
    text_val=st.text(alphabet=SAFE_ALPHABET, min_size=1, max_size=20),
    email_val=st.emails(),
    url_val=st.from_regex(r"https?://[a-z0-9]+\.[a-z]{2,4}", fullmatch=True),
    password_val=st.text(alphabet=SAFE_ALPHABET, min_size=1, max_size=20),
    number_val=st.integers(min_value=1, max_value=100),
)
@HYPOTHESIS_SETTINGS
def test_text_input_types_submission(page: Page, live_server, text_val, email_val, url_val, password_val, number_val):
    """
    Test that various input types (text, email, url, password, number)
    correctly accept values and submit them to the backend.
    """
    url = live_server.url + reverse("text_input_types")
    page.goto(url)

    page.locator("#id_text").fill(text_val)
    page.locator("#id_email").fill(email_val)
    page.locator("#id_url").fill(url_val)
    page.locator("#id_password").fill(password_val)
    page.locator("#id_number").fill(str(number_val))

    page.locator("#submit-types").click()

    expect(page.locator("#success-msg")).to_be_visible()
    success_text = page.locator("#success-msg").inner_text()
    assert f"text_field: {text_val}" in success_text
    assert f"email_field: {email_val}" in success_text
    assert f"url_field: {url_val}" in success_text
    assert f"password_field: {password_val}" in success_text
    assert f"number_field: {number_val}" in success_text


@pytest.mark.django_db
def test_text_input_required_attribute(page: Page, live_server):
    """
    Test that the 'required' attribute is present and enforced by the browser.
    """
    url = live_server.url + reverse("text_input_attributes")
    page.goto(url)

    # Check for the asterisk in the label
    label = page.locator("label[for='id_required']")
    expect(label).to_contain_text("*")

    # Check the 'required' attribute on the input
    input_field = page.locator("#id_required")
    expect(input_field).to_have_attribute("required", "")

    # Try to submit without filling the required field
    page.locator("#submit-attributes").click()

    # Success message should NOT be visible because browser validation should block it
    expect(page.locator("#success-msg")).not_to_be_visible()


@pytest.mark.django_db
def test_text_input_disabled_attribute(page: Page, live_server):
    """
    Test that the 'disabled' attribute is present and prevents interaction.
    """
    url = live_server.url + reverse("text_input_attributes")
    page.goto(url)

    input_field = page.locator("#id_disabled")
    expect(input_field).to_be_disabled()
    expect(input_field).to_have_value("Cannot change me")

    # Attempting to fill a disabled field should raise an error in Playwright,
    # but we can also just verify the attribute.
    expect(input_field).to_have_attribute("disabled", "")


@pytest.mark.django_db
@given(
    short_val=st.text(alphabet=SAFE_ALPHABET, min_size=1, max_size=4),
    long_val=st.text(alphabet=SAFE_ALPHABET, min_size=11, max_size=20),
    valid_val=st.text(alphabet=SAFE_ALPHABET, min_size=5, max_size=10),
)
@HYPOTHESIS_SETTINGS
def test_text_input_length_constraints(page: Page, live_server, short_val, long_val, valid_val):
    """
    Test that 'minlength' and 'maxlength' attributes are present and enforced.
    Note: 'maxlength' prevents typing more characters in most browsers.
    'minlength' is caught during form submission.
    """
    url = live_server.url + reverse("text_input_attributes")
    page.goto(url)

    input_field = page.locator("#id_length")
    expect(input_field).to_have_attribute("minlength", "5")
    expect(input_field).to_have_attribute("maxlength", "10")

    # Fill the required field so it doesn't block us
    page.locator("#id_required").fill("some value")

    # Test short value (violates minlength)
    input_field.fill(short_val)
    page.locator("#submit-attributes").click()
    expect(page.locator("#success-msg")).not_to_be_visible()

    # Test long value (maxlength should truncate it)
    input_field.fill(long_val)
    # The value in the input should be truncated to 10 characters
    expect(input_field).to_have_value(long_val[:10])

    # Test valid value
    input_field.fill(valid_val)
    page.locator("#submit-attributes").click()
    expect(page.locator("#success-msg")).to_be_visible()


@pytest.mark.django_db
def test_text_input_visual_elements(page: Page, live_server):
    """
    Test that visual elements like hint, prefix, and suffix are correctly displayed
    and associated with the input.
    """
    url = live_server.url + reverse("text_input_visual")
    page.goto(url)

    # Hint text
    hint = page.locator("#id_hint-hint")
    expect(hint).to_be_visible()
    expect(hint).to_have_text("This is a helpful hint")
    # In text_input.html it uses aria-describedby="{% if hint %}{{ id }}-hint{% endif %}..."
    # id is id_hint, so it should be id_hint-hint
    expect(page.locator("#id_hint")).to_have_attribute("aria-describedby", "id_hint-hint")

    # Prefix
    expect(page.locator(".govuk-input__prefix").first).to_have_text("£")

    # Suffix
    expect(page.locator(".govuk-input__suffix").first).to_have_text("per month")

    # Label sizes
    expect(page.locator("label[for='id_small_label']")).to_have_class(re.compile(r"govuk-label--s"))
    expect(page.locator("label[for='id_medium_label']")).to_have_class(re.compile(r"govuk-label--m"))
    expect(page.locator("label[for='id_large_label']")).to_have_class(re.compile(r"govuk-label--l"))

    # Placeholder
    expect(page.locator("#id_placeholder")).to_have_attribute("placeholder", "Enter your text here")


@pytest.mark.django_db
def test_text_input_error_states(page: Page, live_server):
    """
    Test that error states correctly apply error classes and display messages.
    """
    url = live_server.url + reverse("text_input_errors")
    page.goto(url)

    # Check input has error class
    expect(page.locator("#id_email")).to_have_class(re.compile(r"govuk-input--error"))

    # Check form group has error class
    expect(page.locator(".govuk-form-group")).to_have_class(re.compile(r"govuk-form-group--error"))

    # Check error summary is visible and contains messages
    error_summary = page.locator(".govuk-error-summary").first
    expect(error_summary).to_be_visible()
    expect(error_summary.locator(".govuk-error-summary__list")).to_contain_text("This field is required")
    expect(error_summary.locator(".govuk-error-summary__list")).to_contain_text("Invalid format")
