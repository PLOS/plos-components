from typing import NamedTuple

from django.utils.safestring import mark_safe
from django_components import types as t, register

from ..base.base_component import PLOSBaseComponent


class MultiSelectionOptionEntry(NamedTuple):
    content: str
    checked: bool = False
    value: str | None = None


@register("_multi_selection")
class _MultiSelectionImpl(PLOSBaseComponent):
    template_name = "multi_selection.html"

    def get_context_data(
            self,
            /,
            *,
            multi_selection_options: list[MultiSelectionOptionEntry],
            # Unique name to identify this multi selection instance.
            name: str | None = None,
            label: str | None = None,
            help_text: str | None = None,
            errors: list[str] | None = None,
            attrs: dict | None = None,
            content_attrs: dict | None = None,
    ):
        if not errors:
            errors = []
        return {
            "attrs": attrs,
            "name": name,
            "multi_selection_options": multi_selection_options,
            "content_attrs": content_attrs,
            "label": label,
            "help_text": help_text,
            "errors": errors,
        }


# This is an "API" component, meaning that it's designed to process
# user input provided as nested components. But after the input is
# processed, it delegates to an internal "implementation" component
# that actually renders the content.
@register("multi_selection")
class MultiSelection(PLOSBaseComponent):
    template: t.django_html = """
    {% load component_tags %}
        {% provide "_multi_selection" multi_selection_options=multi_selection_options errors=errors enabled=True %}
            {% slot "content" default %}{% endslot %}
        {% endprovide %}
    """

    def get_context_data(
            self,
            /,
            *,
            name: str | None = None,
            label: str | None = None,
            help_text: str | None = None,
            errors: list[str] | None = None,
            attrs: dict | None = None,
            content_attrs: dict | None = None,
    ):
        if not name:
            raise RuntimeError(
                    f"You must give the MultiSelection component a name unique to this MultiSelection Component."
            )
        if not errors:
            errors = []
        return {
            "multi_selection_options": [],
            "name": name,
            "attrs": attrs,
            "content_attrs": content_attrs,
            "label": label,
            "help_text": help_text,
            "errors": errors,
        }

    def on_render_after(self, context, template, rendered) -> str:
        """Render the multi selection set.

        By the time we get here, all child multi selection components should have been rendered,
        and they should've populated the multi selection. You must have the context called here to get the population.
        """
        multi_selection_options: list[MultiSelectionOptionEntry] = context["multi_selection_options"]
        errors: list[str] = context["errors"]
        return _MultiSelectionImpl.render(
                kwargs={
                    "multi_selection_options": multi_selection_options,
                    "name": context["name"],
                    "attrs": context["attrs"],
                    "label": context["label"],
                    "help_text": context["help_text"],
                    "errors": errors,
                    "content_attrs": context["content_attrs"],
                },
                render_dependencies=False,
        )


"""
Use this component to define individual multi selection option inside the default slot inside the `multi selection` component.
"""


@register("multi_selection_option")
class MultiSelectionOption(PLOSBaseComponent):
    template: t.django_html = """
    {% load component_tags %}
        {% provide "_multi_selection_option" multi_selection_options=empty_multi_selection_options errors=empty_errors enabled=False %}
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
        # This raises if we're not nested inside the MultiSelection component.
        multi_selection_ctx = self.inject("_multi_selection")

        # We accessed the _multi_selection context, but we're inside ANOTHER multi_selection_option
        if not multi_selection_ctx.enabled:
            raise RuntimeError(
                    f"Component '{self.name}' was called with no parent MultiSelection component. "
                    f"Either wrap '{self.name}' in MultiSelection component, or check if the component "
                    f"is not a descendant of another instance of '{self.name}'"
            )

        if not errors:
            errors = []

        # Do this here to make sure it's added to the parent context.
        parent_multi_selection_errors: list[str] = multi_selection_ctx.errors
        for error in errors:
            parent_multi_selection_errors.append(error)

        return {
            "empty_multi_selection_options": [],
            "empty_errors": [],
            "parent_multi_selection_options": multi_selection_ctx.multi_selection_options,
            "parent_multi_selection_errors": parent_multi_selection_errors,
            "errors": errors,
            "checked": checked,
            "value": value,
        }

    def on_render_after(self, context, template, content):
        parent_multi_selection_options: list[dict] = context["parent_multi_selection_options"]
        parent_multi_selection_options.append({
            "checked": context["checked"],
            "value": context["value"],
            "content": mark_safe(content.strip()),
            "errors": context["errors"],
        })
