"""
A component for rendering a GOV.UK-styled accordion with collapsible sections.

This module provides:
- A parent component that holds and renders all accordion sections.
- A child component for defining each individual section with a heading and content.
"""

from typing import NamedTuple

from django.utils.safestring import mark_safe
from django_components import register
from django_components import types as t

from ..base.base_component import PLOSBaseComponent


class AccordionSectionEntry(NamedTuple):
    """
    Tuples to save content about each section in the accordion.
    """

    heading: str
    content: str
    expanded: bool = False


@register("_plos_accordion")
class _AccordionImpl(PLOSBaseComponent):
    """
    Internal implementation component. Not intended to be used directly.

    Renders the accordion markup from the collected list of sections.
    """

    template_name = "accordion.html"

    def get_context_data(self, /, *, sections: list[AccordionSectionEntry], field_id: str | None = None):  # noqa: D102
        sections_with_index = [
            {
                "heading": section.heading,
                "content": section.content,
                "expanded": section.expanded,
                "index": i + 1,
            }
            for i, section in enumerate(sections)
        ]
        return {"field_id": field_id, "sections": sections_with_index}


@register("plos_accordion")
class Accordion(PLOSBaseComponent):
    """
    An accordion component that groups content into collapsible sections.

    Processes nested plos_accordion_section components and delegates rendering
    to the internal implementation.

    Args:
        field_id (str, optional): Sets the id attribute on the accordion container element.
                                  When provided, section heading and content elements also
                                  receive derived ids (e.g. field_id-heading-1).

    """

    template: t.django_html = """
    {% load component_tags %}
    {% provide "_plos_accordion" sections=sections enabled=True %}
        {% slot "content" default %}{% endslot %}
    {% endprovide %}
    """

    def get_context_data(self, /, *, field_id: str | None = None):  # noqa: D102
        # sections is internal state populated by child AccordionSection components via on_render_after
        return {"field_id": field_id, "sections": []}

    def on_render_after(self, context, template, rendered) -> str:  # noqa: D102
        return _AccordionImpl.render(
            kwargs={
                "field_id": context["field_id"],
                "sections": context["sections"],
            },
            render_dependencies=False,
        )


@register("plos_accordion_section")
class AccordionSection(PLOSBaseComponent):
    """
    Defines an individual section within a plos_accordion component.

    Use this component inside the default slot of plos_accordion to add sections.

    Args:
        heading (str): The section heading displayed in the accordion button.
        expanded (bool, optional): Whether the section is expanded on initial render. Defaults to False.

    """

    template: t.django_html = """
    {% load component_tags %}
    {% provide "_plos_accordion" sections=empty_sections enabled=False %}
        {% slot "content" default %}{% endslot %}
    {% endprovide %}
    """

    def get_context_data(self, /, *, heading: str, expanded: bool = False):  # noqa: D102
        accordion_ctx = self.inject("_plos_accordion")

        if not accordion_ctx.enabled:
            raise RuntimeError(
                f"Component '{self.name}' was called with no parent Accordion component. "
                f"Either wrap '{self.name}' in Accordion component, or check if the component "
                f"is not a descendant of another instance of '{self.name}'"
            )

        return {
            # empty_sections is passed to _plos_accordion's `provide` block because
            # Django templates don't support list literals.
            "empty_sections": [],
            "heading": heading,
            "expanded": expanded,
            "parent_sections": accordion_ctx.sections,
        }

    def on_render_after(self, context, template, content) -> None:  # noqa: D102
        context["parent_sections"].append(
            AccordionSectionEntry(
                heading=context["heading"],
                expanded=context["expanded"],
                content=mark_safe(content.strip()),
            )
        )
