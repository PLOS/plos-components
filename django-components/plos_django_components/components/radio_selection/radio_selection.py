from typing import NamedTuple

from django.utils.safestring import mark_safe
from django_components import types as t, register

from ..base.base_component import PLOSBaseComponent


class RadioSelectionOptionEntry(NamedTuple):
    content: str
    checked: bool = False
    value: str | None = None


@register("_radio_selection")
class _RadioSelectionImpl(PLOSBaseComponent):
    template_name = "radio_selection.html"

    def get_context_data(
            self,
            /,
            *,
            radio_selection_options: list[RadioSelectionOptionEntry],
            # Unique name to identify this radio selection instance.
            name: str | None = "radio_selection",
            legend: str | None = None,
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
            "radio_selection_options": radio_selection_options,
            "content_attrs": content_attrs,
            "legend": legend,
            "hint": hint,
            "errors": errors,
        }


# This is an "API" component, meaning that it's designed to process
# user input provided as nested components. But after the input is
# processed, it delegates to an internal "implementation" component
# that actually renders the content.
@register("radio_selection")
class RadioSelection(PLOSBaseComponent):
    template: t.django_html = """
    {% load component_tags %}
        {% provide "_radio_selection" radio_selection_options=radio_selection_options errors=errors enabled=True %}
            {% slot "content" default %}{% endslot %}
        {% endprovide %}
    """

    def get_context_data(
            self,
            /,
            *,
            name: str | None = None,
            legend: str | None = None,
            hint: str | None = None,
            errors: list[str] | None = None,
            attrs: dict | None = None,
            content_attrs: dict | None = None,
    ):
        if not name:
            raise RuntimeError(
                    f"You must give the RadioSelection component a name unique to this RadioSelection Component."
            )
        if not errors:
            errors = []
        return {
            "radio_selection_options": [],
            "name": name,
            "attrs": attrs,
            "content_attrs": content_attrs,
            "legend": legend,
            "hint": hint,
            "errors": errors,
        }

    def on_render_after(self, context, template, rendered) -> str:
        """Render the radio selection set.

        By the time we get here, all child radio selection components should have been rendered,
        and they should've populated the radio selection. You must have the context called here to get the population.
        """
        radio_selection_options: list[RadioSelectionOptionEntry] = context["radio_selection_options"]
        errors: list[str] = context["errors"]
        return _RadioSelectionImpl.render(
                kwargs={
                    "radio_selection_options": radio_selection_options,
                    "name": context["name"],
                    "attrs": context["attrs"],
                    "legend": context["legend"],
                    "hint": context["hint"],
                    "errors": errors,
                    "content_attrs": context["content_attrs"],
                },
                render_dependencies=False,
        )


"""
Use this component to define individual radio selection option inside the default slot inside the `radio selection` component.
"""
@register("radio_selection_option")
class RadioSelectionOption(PLOSBaseComponent):
    template: t.django_html = """
    {% load component_tags %}
        {% provide "_radio_selection_option" radio_selection_options=empty_radio_selection_options errors=empty_errors enabled=False %}
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
        # This raises if we're not nested inside the RadioSelection component.
        radio_selection_ctx = self.inject("_radio_selection")

        # We accessed the _radio_selection context, but we're inside ANOTHER radio_selection_option
        if not radio_selection_ctx.enabled:
            raise RuntimeError(
                    f"Component '{self.name}' was called with no parent RadioSelection component. "
                    f"Either wrap '{self.name}' in RadioSelection component, or check if the component "
                    f"is not a descendant of another instance of '{self.name}'"
            )

        if not errors:
            errors = []

        # Do this here to make sure it's added to the parent context.
        parent_radio_selection_errors: list[str] = radio_selection_ctx.errors
        for error in errors:
            parent_radio_selection_errors.append(error)

        return {
            "empty_radio_selection_options": [],
            "empty_errors": [],
            "parent_radio_selection_options": radio_selection_ctx.radio_selection_options,
            "parent_radio_selection_errors": parent_radio_selection_errors,
            "errors": errors,
            "checked": checked,
            "value": value,
        }

    def on_render_after(self, context, template, content):
        parent_radio_selection_options: list[dict] = context["parent_radio_selection_options"]
        parent_radio_selection_options.append({
            "checked": context["checked"],
            "value": context["value"],
            "content": mark_safe(content.strip()),
            "errors": context["errors"],
        })

