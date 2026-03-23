"""
A base component which provides the CSS and JS for all components.
"""

from django.utils.safestring import mark_safe
from django_components import Component


class PLOSBaseComponent(Component):
    """
    A base component which provides the CSS and JS for all components.
    """

    class Media:
        """
        The media for this component.
        """

        css = [
            "https://ux.plos.org/assets/v3/styles/gov-uk-frontend-v6.min.css",
            "https://ux.plos.org/assets/v3/styles/plos-overrides.min.css",
        ]
        js = [
            mark_safe(
                """
                    <script>
      document.body.className +=
        " js-enabled" +
        ("noModule" in HTMLScriptElement.prototype
          ? " govuk-frontend-supported"
          : "");
    </script>
                    """
            ),
            mark_safe(
                """
<script type="module">
      import { initAll } from "https://ux.plos.org/assets/v3/scripts/gov-uk-frontend-v6.min.js";
      initAll();
    </script>
                    """
            ),
        ]
