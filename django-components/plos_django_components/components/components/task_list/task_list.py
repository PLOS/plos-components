"""
A component function which provides the ability to display a list of tasks with their statuses.

This module provides:
- A parent task list component.
- A task list item component for individual tasks.
"""

from typing import NamedTuple

from django.template import Context, Template
from django.utils.safestring import mark_safe
from django_components import register
from django_components import types as t

from ..base.base_component import PLOSBaseComponent


class TaskListItemDetails(NamedTuple):
    """
    Tuples to save content about each entry in the task list items.
    """

    label: str
    url: str
    status: str
    color: str
    attrs: dict | None = None


@register("_plos_task_list")
class _TaskListImpl(PLOSBaseComponent):
    template_name = "components/task_list/task_list.html"

    def get_context_data(
        self,
        /,
        *,
        id: str,
        task_list_items: list[TaskListItemDetails],
        attrs: dict | None = None,
    ):
        return {
            "id": id,
            "attrs": attrs,
            "task_list_items": task_list_items,
        }


@register("plos_task_list")
class TaskList(PLOSBaseComponent):
    """
    The task list parent component.
    """

    template: t.django_html = """
    {% load component_tags %}
        {% provide "_plos_task_list" task_list_items=task_list_items enabled=True %}
            {% slot "content" default %}{% endslot %}
        {% endprovide %}
    """

    def get_context_data(self, /, *, id, attrs: dict | None = None):
        return {
            "id": id,
            "task_list_items": [],
            "attrs": attrs,
        }

    def on_render_after(self, context: Context, template: Template | None, rendered) -> str:
        """
        Render the task list set.

        By the time we get here, all child task list item components should have been rendered,
        and they should've populated the task list items.

        :param rendered: The elements already rendered.
        :param context: The context of the rendering.
        :param template: The template to render.
        """
        task_list_items: list[TaskListItemDetails] = context["task_list_items"]

        return _TaskListImpl.render(
            kwargs={
                "id": context["id"],
                "task_list_items": task_list_items,
                "attrs": context["attrs"],
            },
            render_dependencies=False,
        )


@register("plos_task_list_item")
class TaskListItem(PLOSBaseComponent):
    """
    Use this component to define individual task list items inside the default slot inside the `task list`
    component.
    """

    template: t.django_html = """
    {% load component_tags %}
        {% provide "_plos_task_list_item" task_list_items=empty_task_list_items enabled=False %}
            {% slot "content" default %}{% endslot %}
        {% endprovide %}
    """

    def get_context_data(
        self,
        /,
        *,
        label: str,
        status: str,
        color: str | None = None,
        url: str | None = None,
        attrs: dict | None = None,
    ):
        # Access the list of items registered for parent task list component
        # This raises if we're not nested inside the TaskList component.
        task_list_ctx = self.inject("_plos_task_list")

        # We accessed the _plos_task_list context, but we're inside ANOTHER plos_task_list_item
        if not task_list_ctx.enabled:
            raise RuntimeError(
                f"Component '{self.name}' was called with no parent TaskList component. "
                f"Either wrap '{self.name}' in TaskList component, or check if the component "
                f"is not a descendant of another instance of '{self.name}'"
            )

        return {
            "empty_task_list_items": [],
            "parent_task_list_items": task_list_ctx.task_list_items,
            "label": label,
            "status": status,
            "color": color,
            "url": url,
            "attrs": attrs,
        }

    def on_render_after(self, context, template, content):  # noqa: D102
        parent_task_list_items: list[dict] = context["parent_task_list_items"]
        parent_task_list_items.append(
            {
                "label": context["label"],
                "url": context["url"],
                "status": context["status"],
                "color": context["color"],
                "attrs": context["attrs"],
            }
        )
