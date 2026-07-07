from django_components import register

from ..base.base_component import PLOSBaseComponent


@register("plos_text_group")
class TextGroup(PLOSBaseComponent):
    """
    Groups related paragraphs so they read as one block.

    Wraps its slotted content so the text within sits 16px apart, while the
    group is separated from surrounding content by the 32px margin-bottom.

    Example usage:

        {% component "plos_text_group" %}
            {% component "plos_text_box" %}First paragraph.{% endcomponent %}
            {% component "plos_text_box" %}Second paragraph.{% endcomponent %}
        {% endcomponent %}
    """

    template_name = "text_group.html"
