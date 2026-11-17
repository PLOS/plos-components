"""
A component for rendering a modal.

This module provides:
- A modal dialog that works with or without JavaScript.
"""

from typing import Literal

from django_components import register

from ..base.base_component import PLOSBaseComponent

# The plos_button classes for each `action`
BUTTON_CLASSES = {
    "primary": "govuk-button",
    "secondary": "govuk-button govuk-button--secondary",
    "warning": "govuk-button govuk-button--warning",
}


@register("plos_modal")
class Modal(PLOSBaseComponent):
    """
    A modal dialog with its own trigger and Cancel button.

    Without JavaScript it renders as a `<details>` that expands inline, and only
    one modal on the page is open at a time.

    With JavaScript, `modal.js` turns the component into a `<button>` and a `<dialog>`.

    Args:
        describe_body (bool): Use the body as the accessible description, so
            screen readers read it when the modal opens. For short
            confirmations, not long content.
        alert (bool): Use `role="alertdialog"` for a confirmation that needs a
            response, like deleting something. Turns on `describe_body`. Not
            for long content or forms. Without JavaScript the content is a
            group.
        trigger_class (str): Classes that replace the trigger's button style,
            for patterns with their own trigger, like add more's delete link.
        trigger_label (str): The trigger's plain-text name, for the line
            without JavaScript that says "To cancel, select <trigger_label>
            again". Defaults to `trigger`. Pass it when you fill the `trigger`
            slot, or the line is left out.
        cancel_field_name (str), cancel_value (str): Without JavaScript,
            replace that line with a Cancel button that submits the form with
            this name and value. The view must re-render the page without
            validating or saving; the modal then renders closed. Pair it with
            `trigger_autofocus`.
        trigger_autofocus (bool): Without JavaScript, focus the trigger on page
            load, for example after that Cancel button reloads the page.
        heading_level (int): The title's heading level (2 to 4). Without
            JavaScript the title is part of the page, so set it to fit the
            headings around it.
        enter_submits (str): Enter in a field clicks the form's first submit
            button, even one inside a closed modal. The modal renders a hidden
            submit button with this name first, so Enter never presses the
            confirm button. Set it to the page's main submit button name.
            Pass None when the modal is not in a form, or an earlier submit
            button already handles Enter.

    Slots:
        trigger: Trigger content, for example with an icon. Use it instead of
            `trigger`.
        default: The modal body. It scrolls when the content is taller than
            the maximum height.
        actions: The buttons, rendered in a button group at the bottom.

    Example usage::

        {% component "plos_modal" field_id="deactivate" title="Deactivate account" alert=True
            trigger="Deactivate account" trigger_action="warning" %}
          {% fill "default" %}
            {% component "plos_text_box" %}Are you sure you want to deactivate your account?{% endcomponent %}
          {% endfill %}
          {% fill "actions" %}
            {% component "plos_button" action="warning" button_type="submit" field_name="deactivate" value="yes" %}
              Deactivate
            {% endcomponent %}
          {% endfill %}
        {% endcomponent %}
    """

    template_name = "modal.html"

    class Media:
        js = ["plos_django_components/modal.js"]

    def get_context_data(  # noqa: D102
        self,
        /,
        *,
        field_id: str,
        title: str,
        size: Literal["xs", "sm", "md", "lg"] = "sm",
        describe_body: bool = False,
        alert: bool = False,
        trigger: str | None = None,
        trigger_action: Literal["primary", "secondary", "warning"] = "primary",
        trigger_class: str | None = None,
        trigger_label: str | None = None,
        cancel_label: str = "Cancel",
        cancel_field_name: str | None = None,
        cancel_value: str = "cancel",
        trigger_autofocus: bool = False,
        heading_level: Literal[2, 3, 4] = 2,
        enter_submits: str | None = "continue",
    ):
        if not trigger and "trigger" not in self.input.slots:
            raise ValueError(
                f"plos_modal '{field_id}' needs a trigger: pass `trigger` or fill the `trigger` slot")
        return {
            "field_id": field_id,
            "title": title,
            "size": size,
            "describe_body": describe_body or alert,
            "alert": alert,
            "trigger": trigger,
            "trigger_class": trigger_class or BUTTON_CLASSES[trigger_action],
            "trigger_label": trigger_label or trigger,
            "cancel_label": cancel_label,
            "cancel_field_name": cancel_field_name,
            "cancel_value": cancel_value,
            "trigger_autofocus": trigger_autofocus,
            "heading_level": heading_level,
            "title_id": f"{field_id}-title",
            # plos_button_group's own field_id shadows ours inside it
            "modal_id": field_id,
            "no_js_cancel_id": f"{field_id}-cancel-no-js",
            "enter_submits": enter_submits,
        }
