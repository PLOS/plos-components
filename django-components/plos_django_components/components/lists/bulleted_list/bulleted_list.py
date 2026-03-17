from typing import NamedTuple

from django.utils.safestring import mark_safe
from django_components import types as t, Component, register


class BulletedListOptionEntry(NamedTuple):
    content: str
    field_id: str | None = None


@register("_bulleted_list")
class _BulletedListImpl(Component):
    template_name = "bulleted_list.html"

    def get_context_data(
            self,
            /,
            *,
            options: list[BulletedListOptionEntry],
            # Unique name to identify this component instance.
            name: str | None = None,
            label: str | None = None,
            attrs: dict | None = None,
            content_attrs: dict | None = None,
    ):
        return {
            "attrs": attrs,
            "name": name,
            "options": options,
            "content_attrs": content_attrs,
            "label": label,
        }


# This is an "API" component, meaning that it's designed to process
# user input provided as nested components. But after the input is
# processed, it delegates to an internal "implementation" component
# that actually renders the content.
@register("bulleted_list")
class BulletedList(Component):
    template: t.django_html = """
    {% load component_tags %}
        {% provide "_bulleted_list" options=options enabled=True %}
            {% slot "content" default %}{% endslot %}
        {% endprovide %}
    """

    def get_context_data(
            self,
            /,
            *,
            name: str | None = None,
            label: str | None = None,
            attrs: dict | None = None,
            content_attrs: dict | None = None,
    ):
        return {
            "options": [],
            "name": name,
            "attrs": attrs,
            "content_attrs": content_attrs,
            "label": label,
        }

    def on_render_after(self, context, template, rendered) -> str:
        """Render the bulleted list set.

        By the time we get here, all child bulleted list components should have been rendered,
        and they should've populated the bulleted list. You must have the context called here to get the population.
        """
        options: list[BulletedListOptionEntry] = context["options"]
        return _BulletedListImpl.render(
                kwargs={
                    "options": options,
                    "name": context["name"],
                    "attrs": context["attrs"],
                    "label": context["label"],
                    "content_attrs": context["content_attrs"],
                },
                render_dependencies=False,
        )


"""
Use this component to define individual component option inside the default slot inside the component.
"""
@register("bulleted_list_option")
class BulletedListOption(Component):
    template: t.django_html = """
    {% load component_tags %}
        {% provide "_bulleted_list_option" options=empty_options enabled=False %}
            {% slot "content" default %}{% endslot %}
        {% endprovide %}
    """

    def get_context_data(
            self,
            /,
            *,
            field_id: str | None = None,
    ):
        # Access the list of options registered for parent options component
        # This raises if we're not nested inside the parent component.
        parent_ctx = self.inject("_bulleted_list")

        # We accessed the _bulleted_list context, but we're inside ANOTHER bulleted_list_option
        if not parent_ctx.enabled:
            raise RuntimeError(
                    f"Component '{self.name}' was called with no parent BulletedList component. "
                    f"Either wrap '{self.name}' in BulletedList component, or check if the component "
                    f"is not a descendant of another instance of '{self.name}'"
            )

        return {
            "empty_options": [],
            "parent_options": parent_ctx.options,
            "field_id": field_id,
        }

    def on_render_after(self, context, template, content):
        parent_options: list[dict] = context["parent_options"]
        parent_options.append({
            "field_id": context["field_id"],
            "content": mark_safe(content.strip()),
        })
