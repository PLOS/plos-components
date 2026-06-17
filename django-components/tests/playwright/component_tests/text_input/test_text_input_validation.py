import pytest
from django.urls import reverse
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from playwright.sync_api import Page, expect

# Use a reasonably small number of examples for Playwright tests to avoid excessive runtimes
HYPOTHESIS_SETTINGS = settings(
    max_examples=10, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture]
)


@pytest.mark.django_db
@given(val=st.decimals(min_value=0, max_value=100, places=1).filter(lambda x: x % 1 != 0))
@HYPOTHESIS_SETTINGS
def test_text_input_step_validation_decimal(page: Page, live_server, val):
    """
    Test that decimal values are handled correctly:
    - With step="1": Browser validation should block form submission.
    - Without step (default "any"): Browser validation should NOT block form submission,
      allowing for on-brand PLOS error messages from the backend.
    """
    url = live_server.url + reverse("text_input_validation")
    page.goto(url)

    # Use '{:.1f}'.format(val) to ensure we have a decimal point even if it ends in .0
    # although our filter(lambda x: x % 1 != 0) should prevent that.
    # Still, str(Decimal('1.3')) is '1.3', which is fine.
    str_val = f"{val:.1f}"

    # 1. Test with step="1" (should be blocked by browser)
    input_step_one = page.locator("#id_age_step_one")
    input_step_one.fill(str_val)

    page.locator("#submit-step-1").click()

    # The browser validation should prevent the form from being submitted.
    expect(page.locator("#success-msg")).not_to_be_visible()

    # 2. Test without step (default "any", should NOT be blocked)
    input_step_any = page.locator("#id_age_step_any")
    input_step_any.fill(str_val)

    page.locator("#submit-step-any").click()

    # This should submit successfully to the backend.
    expect(page.locator("#success-msg")).to_be_visible()
    expect(page.locator("#success-msg")).to_contain_text(f"Submitted step_any with value: {str_val}")

    # Check for on-brand error summary
    expect(page.locator(".govuk-error-summary")).to_be_visible()
    expect(page.locator(".govuk-error-summary .govuk-error-summary__list")).to_contain_text("Enter a whole number")


@pytest.mark.django_db
@given(val=st.integers(min_value=0, max_value=100))
@HYPOTHESIS_SETTINGS
def test_text_input_step_validation_whole_number(page: Page, live_server, val):
    """
    Test that whole numbers are accepted in both cases.
    """
    url = live_server.url + reverse("text_input_validation")
    page.goto(url)

    str_val = str(val)

    # 1. Test with step="1" with whole number
    input_step_one = page.locator("#id_age_step_one")
    input_step_one.fill(str_val)
    page.locator("#submit-step-1").click()

    expect(page.locator("#success-msg")).to_be_visible()
    expect(page.locator("#success-msg")).to_contain_text(f"Submitted step_one with value: {str_val}")

    # 2. Test without step with whole number
    input_step_any = page.locator("#id_age_step_any")
    input_step_any.fill(str_val)
    page.locator("#submit-step-any").click()

    expect(page.locator("#success-msg")).to_be_visible()
    expect(page.locator("#success-msg")).to_contain_text(f"Submitted step_any with value: {str_val}")
