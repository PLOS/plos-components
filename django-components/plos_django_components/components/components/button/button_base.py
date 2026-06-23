"""
A component function which provides the ability to create a button on any web page.

This module provides:
- A button that can be displayed on any web page.
- HTMX options for partial page updates without a full page reload.
"""

from typing import Literal

from django_components import register

from ..base.base_component import PLOSBaseComponent


@register("plos_button")
class Button(PLOSBaseComponent):
    """
    A button that can be displayed on any web page.

    When the HTMX parameters are provided they are rendered as `hx-post`,
    `hx-target`, `hx-swap`, and `hx-include` attributes on the `<button>`
    element, enabling partial page updates without a full page reload. Omit
    all four for a plain form submit button.

    Example usage::

        {# Plain form submit #}
        {% component "plos_button" button_type="submit" action="primary" %}
          {% fill "default" %}Save{% endfill %}
        {% endcomponent %}

        {# An HTMX partial update posts to the URL and swaps only the target container #}
        {% component "plos_button"
          button_type="submit"
          action="secondary"
          hx_post="/my-url/"
          hx_target="#my-container"
          hx_swap="outerHTML"
          hx_include="#my-container"
        %}
          {% fill "default" %}Add another{% endfill %}
        {% endcomponent %}
    """

    template_name = "button_base.html"

    def get_context_data(  # noqa: D102
        self,
        /,
        *,
        disabled: bool = False,
        action: Literal["primary", "secondary", "warning"] = "primary",
        button_type: Literal["button", "reset", "submit"] = "button",
        icon: str | None = None,
        icon_position: Literal["right", "left"] = "right",
        value: str | None = None,
        form_action: str | None = None,
        field_id: str | None = None,
        field_name: str | None = None,
        href: str | None = None,
        hx_post: str | None = None,
        hx_target: str | None = None,
        hx_swap: str | None = None,
        hx_include: str | None = None,
        hx_select: str | None = None,
        hx_disabled_elt: str | None = None,
        hx_sync: str | None = None,
        autofocus: bool = False,
        **kwargs,
    ):
        if href == "":
            href = None

        context = {
            "disabled": disabled,
            "action": action,
            "button_type": button_type,
            "icon": icon,
            "icon_position": icon_position,
            "value": value,
            "form_action": form_action,
            "field_id": field_id,
            "field_name": field_name,
            "href": href,
            "hx_post": hx_post,
            "hx_target": hx_target,
            "hx_swap": hx_swap,
            "hx_include": hx_include,
            "hx_select": hx_select,
            "hx_disabled_elt": hx_disabled_elt,
            "hx_sync": hx_sync,
            "autofocus": autofocus,
        }
        context.update(kwargs)
        return context
