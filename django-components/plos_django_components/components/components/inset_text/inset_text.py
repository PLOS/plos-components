"""
Inset text styled component.
"""

from django_components import register

from ..base.base_component import PLOSBaseComponent


@register("plos_inset_text")
class InsetText(PLOSBaseComponent):
    """
    An inset text styled component. Good for displaying quotes.
    """

    template_name = "inset_text.html"

    def get_context_data(self):
        return {}
