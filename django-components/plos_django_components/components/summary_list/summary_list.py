"""
A component function which provides the ability to review answers after completing a form.

This module provides:
- A parent component for defining where a table should begin
- A child component for defining each answer and the actions a user may take upon an action, if any.
"""

from typing import NamedTuple

from django.utils.safestring import mark_safe
from django_components import register
from django_components import types as t

from ..base.base_component import PLOSBaseComponent


class SummaryListActionTuple(NamedTuple):
    """
    Defines the action for each answer a user can check.

    @:param name The name of the action, will be shown to users.
    @:param url The URL of the action the user will be taken to complete.
    """

    name: str | None
    url: str | None


class SummaryListEntry(NamedTuple):
    """
    Tuples to save content about each entry in the options.
    """

    key: str | None
    content: str
    actions: list[dict] | None
    errors: list[str] | None


@register("_plos_summary_list")
class _SummaryListImpl(PLOSBaseComponent):
    """
    The hidden parent component.
    """

    template_name = "summary_list.html"

    def get_context_data(
        self,
        /,
        *,
        item_options: list[SummaryListEntry],
        name: str | None = None,
        errors: list[str] | None = None,
        attrs: dict | None = None,
        content_attrs: dict | None = None,
        field_id: str | None = None,
    ):
        if not errors:
            errors = []

        if not field_id:
            field_id = name

        return {
            "attrs": attrs,
            "name": name,
            "item_options": item_options,
            "content_attrs": content_attrs,
            "errors": errors,
            "field_id": field_id,
        }


@register("plos_summary_list")
class SummaryList(PLOSBaseComponent):
    """
    An "API" component, meaning that it's designed to process user input provided as nested components.

    But after the input is processed, it delegates to an internal "implementation" component that actually renders the
    content.
    """

    template: t.django_html = """
    {% load component_tags %}
        {% provide "_plos_summary_list" item_options=item_options errors=errors enabled=True %}
            {% slot "content" default %}{% endslot %}
        {% endprovide %}
    """

    def get_context_data(  # noqa: D102
        self,
        /,
        *,
        errors: list[str] | None = None,
        attrs: dict | None = None,
        content_attrs: dict | None = None,
        field_id: str | None = None,
    ):
        if not errors:
            errors = []

        return {
            "item_options": [],
            "attrs": attrs,
            "content_attrs": content_attrs,
            "errors": errors,
            "field_id": field_id,
        }

    def on_render_after(self, context, template, rendered) -> str:  # noqa: D102
        item_options: list[SummaryListEntry] = context["item_options"]
        errors: list[str] = context["errors"]
        return _SummaryListImpl.render(
            kwargs={
                "item_options": item_options,
                "attrs": context["attrs"],
                "errors": errors,
                "content_attrs": context["content_attrs"],
                "field_id": context["field_id"],
            },
            render_dependencies=False,
        )


@register("plos_summary_list_option")
class SummaryListOption(PLOSBaseComponent):
    """
    Use this component to define individual summary list option inside the default slot inside the `summary list`
    component.
    """

    template: t.django_html = """
    {% load component_tags %}
        {% provide "_plos_summary_list_option" item_options=empty_item_options errors=empty_errors enabled=False %}
            {% slot "content" default %}{% endslot %}
        {% endprovide %}
    """

    def get_context_data(  # noqa: D102
        self,
        /,
        *,
        key: str | None = None,
        errors: list[str] | None = None,
        actions: list[dict] | None = None,
    ):
        # Access the list of options registered for parent options component
        # This raises if we're not nested inside the parent component.
        parent_ctx = self.inject("_plos_summary_list")

        # We accessed the _item_options context, but we're inside ANOTHER item_options_option
        if not parent_ctx.enabled:
            raise RuntimeError(
                f"Component '{self.name}' was called with no parent Summary List component. "
                f"Either wrap '{self.name}' in Summary List component, or check if the component "
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
            "key": key,
            "errors": errors,
            "actions": actions,
        }

    def on_render_after(self, context, template, content):  # noqa: D102
        parent_options: list[dict] = context["parent_options"]
        parent_options.append(
            {
                "content": mark_safe(content.strip()),
                "actions": context["actions"],
                "errors": context["errors"],
                "key": context["key"],
            }
        )
