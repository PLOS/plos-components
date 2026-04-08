"""
A component function which provides the ability to create an ordered, numbered list.

This module provides:
- A parent holding the list entries.
- A child element for each entry.
"""

from typing import NamedTuple

from django.utils.safestring import mark_safe
from django_components import register
from django_components import types as t

from ...base.base_component import PLOSBaseComponent


class OrderedListOptionEntry(NamedTuple):
    """
    Tuples to save content about each entry in the options.
    """

    content: str
    field_id: str | None = None


@register("_plos_ordered_list")
class _OrderedListImpl(PLOSBaseComponent):
    template_name = "ordered_list.html"

    def get_context_data(
        self,
        /,
        *,
        options: list[OrderedListOptionEntry],
        # Unique name to identify this component instance.
        name: str | None = None,
        attrs: dict | None = None,
        content_attrs: dict | None = None,
        # Note: field_id and an "id" key in attrs are mutually exclusive. If both are
        # provided, the template will render two id attributes on the <ul> element,
        # which is invalid HTML. Use field_id for the container id, not attrs.
        field_id: str | None = None,
    ):
        return {
            "attrs": attrs,
            "name": name,
            "options": options,
            "content_attrs": content_attrs,
            "field_id": field_id,
        }


@register("plos_ordered_list")
class OrderedList(PLOSBaseComponent):
    """
    An "API" component, meaning that it's designed to process user input provided as nested components.

    But after the input is processed, it delegates to an internal "implementation" component that actually renders the content.
    """

    template: t.django_html = """
    {% load component_tags %}
        {% provide "_plos_ordered_list" options=options enabled=True %}
            {% slot "content" default %}{% endslot %}
        {% endprovide %}
    """

    def get_context_data(  # noqa: D102
        self,
        /,
        *,
        name: str | None = None,
        attrs: dict | None = None,
        content_attrs: dict | None = None,
        field_id: str | None = None,
    ):
        return {
            "options": [],
            "name": name,
            "attrs": attrs,
            "content_attrs": content_attrs,
            "field_id": field_id,
        }

    def on_render_after(self, context, template, rendered) -> str:  # noqa: D102
        options: list[OrderedListOptionEntry] = context["options"]
        return _OrderedListImpl.render(
            kwargs={
                "options": options,
                "name": context["name"],
                "attrs": context["attrs"],
                "content_attrs": context["content_attrs"],
                "field_id": context["field_id"],
            },
            render_dependencies=False,
        )


@register("plos_ordered_list_option")
class OrderedListOption(PLOSBaseComponent):
    """
    Use this component to define individual component option inside the default slot inside the component.
    """

    template: t.django_html = """
    {% load component_tags %}
        {% provide "_plos_ordered_list_option" options=empty_options enabled=False %}
            {% slot "content" default %}{% endslot %}
        {% endprovide %}
    """

    def get_context_data(  # noqa: D102
        self,
        /,
        *,
        field_id: str | None = None,
    ):
        # Access the list of options registered for parent options component
        # This raises if we're not nested inside the parent component.
        parent_ctx = self.inject("_plos_ordered_list")

        # We accessed the _plos_ordered_list context, but we're inside ANOTHER plos_ordered_list_option
        if not parent_ctx.enabled:
            raise RuntimeError(
                f"Component '{self.name}' was called with no parent OrderedList component. "
                f"Either wrap '{self.name}' in OrderedList component, or check if the component "
                f"is not a descendant of another instance of '{self.name}'"
            )

        return {
            "empty_options": [],
            "parent_options": parent_ctx.options,
            "field_id": field_id,
        }

    def on_render_after(self, context, template, content):  # noqa: D102
        parent_options: list[OrderedListOptionEntry] = context["parent_options"]
        parent_options.append(
            OrderedListOptionEntry(
                field_id=context["field_id"],
                content=mark_safe(content.strip()),
            )
        )
