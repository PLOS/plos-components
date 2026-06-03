"""
A component which renders a dynamic back link.

Use above the main content area to let users navigate to the previous page.
"""
from django_components import register

from ..base.base_component import PLOSBaseComponent


@register("plos_back_link")
class BackLink(PLOSBaseComponent):
    """
    Renders a dynamic back link.

    Parameters:

        href    URL the link points to (default: "#")
        text    visible link text (default: "Back")

    Example usage:

        {% component "plos_back_link" href=back_url %}{% endcomponent %}
    """

    template_name = "back_link.html"

    def get_context_data(
        self,
        href: str = "#",
        text: str = "Back",
    ):
        return {
            "href": href,
            "text": text,
        }
