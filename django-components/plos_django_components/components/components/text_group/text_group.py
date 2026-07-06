from django_components import register

from ..base.base_component import PLOSBaseComponent


@register("plos_text_group")
class TextGroup(PLOSBaseComponent):
    """
    Groups related paragraphs so they read as one block.

    Wraps its slotted content so the body paragraphs inside sit 8px apart, and the
    group as a whole sits 32px below (the standard between-group gap). Use it around
    two or more related text boxes that should read together, separated from
    surrounding content by the 32px rhythm.

    Example usage:

        {% component "plos_text_group" %}
            {% component "plos_text_box" %}First paragraph.{% endcomponent %}
            {% component "plos_text_box" %}Second paragraph.{% endcomponent %}
        {% endcomponent %}
    """

    template_name = "text_group.html"
