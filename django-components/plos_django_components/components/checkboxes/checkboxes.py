from typing import Literal, NamedTuple

from django.utils.safestring import mark_safe
from django_components import register
from django_components import types as t

from ..base.base_component import PLOSBaseComponent


class CheckboxesEntry(NamedTuple):
    content: str
    checked: bool = False
    value: str | None = None


@register("_plos_checkboxes")
class _CheckboxesImpl(PLOSBaseComponent):
    template_name = "checkboxes.html"

    def get_context_data(
        self,
        /,
        *,
        item_options: list[CheckboxesEntry],
        name: str | None = None,
        legend: str | None = None,
        legend_size: Literal["large", "medium", "small"] = "small",
        hint: str | None = None,
        errors: list[str] | None = None,
        attrs: dict | None = None,
        content_attrs: dict | None = None,
    ):
        if not errors:
            errors = []
        return {
            "attrs": attrs,
            "name": name,
            "item_options": item_options,
            "content_attrs": content_attrs,
            "legend": legend,
            "legend_size": legend_size,
            "hint": hint,
            "errors": errors,
        }


# This is an "API" component, meaning that it's designed to process
# user input provided as nested components. But after the input is
# processed, it delegates to an internal "implementation" component
# that actually renders the content.
@register("plos_checkboxes")
class Checkboxes(PLOSBaseComponent):
    template: t.django_html = """
    {% load component_tags %}
        {% provide "_plos_checkboxes" item_options=item_options errors=errors enabled=True %}
            {% slot "content" default %}{% endslot %}
        {% endprovide %}
    """

    def get_context_data(
        self,
        /,
        *,
        name: str | None = None,
        legend: str | None = None,
        legend_size: Literal["large", "medium", "small"] = "small",
        hint: str | None = None,
        errors: list[str] | None = None,
        attrs: dict | None = None,
        content_attrs: dict | None = None,
    ):
        if not name:
            raise RuntimeError(
                "You must give the Checkbox component a name unique to this Checkbox Component."
            )
        if not errors:
            errors = []
        return {
            "item_options": [],
            "name": name,
            "attrs": attrs,
            "content_attrs": content_attrs,
            "legend": legend,
            "legend_size": legend_size,
            "hint": hint,
            "errors": errors,
        }

    def on_render_after(self, context, template, rendered) -> str:
        """Render the checkbox set.

        By the time we get here, all child checkbox components should have been rendered,
        and they should've populated the checkbox. You must have the context called here to get the population.
        """
        item_options: list[CheckboxesEntry] = context["item_options"]
        errors: list[str] = context["errors"]
        return _CheckboxesImpl.render(
            kwargs={
                "item_options": item_options,
                "name": context["name"],
                "attrs": context["attrs"],
                "legend": context["legend"],
                "hint": context["hint"],
                "legend_size": context["legend_size"],
                "errors": errors,
                "content_attrs": context["content_attrs"],
            },
            render_dependencies=False,
        )


"""
Use this component to define individual checkboxes option inside the default slot inside the `checkboxes` component.
"""


@register("plos_checkboxes_option")
class CheckboxesOption(PLOSBaseComponent):
    template: t.django_html = """
    {% load component_tags %}
        {% provide "_plos_checkboxes_option" item_options=empty_item_options errors=empty_errors enabled=False %}
            {% slot "content" default %}{% endslot %}
        {% endprovide %}
    """

    def get_context_data(
        self,
        /,
        *,
        value: str | None = None,
        errors: list[str] | None = None,
        checked: bool = False,
    ):
        # Access the list of options registered for parent options component
        # This raises if we're not nested inside the Checkboxes component.
        parent_ctx = self.inject("_plos_checkboxes")

        # We accessed the _item_options context, but we're inside ANOTHER item_options_option
        if not parent_ctx.enabled:
            raise RuntimeError(
                f"Component '{self.name}' was called with no parent Checkboxes component. "
                f"Either wrap '{self.name}' in Checkboxes component, or check if the component "
                f"is not a descendant of another instance of '{self.name}'"
            )

        if not errors:
            errors = []

        # Do this here to make sure it's added to the parent context.
        parent_errors: list[str] = parent_ctx.errors
        for error in errors:
            parent_errors.append(error)

        return {
            "empty_item_options": [],
            "empty_errors": [],
            "parent_options": parent_ctx.item_options,
            "parent_errors": parent_errors,
            "errors": errors,
            "checked": checked,
            "value": value,
        }

    def on_render_after(self, context, template, content):
        parent_options: list[dict] = context["parent_options"]
        parent_options.append(
            {
                "checked": context["checked"],
                "value": context["value"],
                "content": mark_safe(content.strip()),
                "errors": context["errors"],
            }
        )
