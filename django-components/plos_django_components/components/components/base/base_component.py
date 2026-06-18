"""
A base component which provides the CSS and JS for all components.
"""

from django.conf import settings
from django.utils.safestring import SafeString, mark_safe
from django_components import Component

from .icon_fonts.base_icon import IconFontSetting

primary_css: str | None = getattr(settings, "GOV_UK_TEMPLATE_PRIMARY_CSS", None)
override_css: list[str] | str | None = getattr(settings, "GOV_UK_TEMPLATE_OVERRIDE_CSS", None)
primary_js: str | None = getattr(settings, "GOV_UK_TEMPLATE_PRIMARY_JS", None)


def get_css() -> list[str | SafeString]:
    """
    Gets the CSS items for the base components.
    """
    templates: list[str | SafeString] = [IconFontSetting().fetch_icon_font_stylesheet()]

    if primary_css is None:
        return templates

    templates.append(primary_css)

    if override_css is not None:
        if isinstance(override_css, str):
            templates.append(override_css)
        else:
            for template in override_css:
                templates.append(template)

    return templates


def get_js() -> list[str | SafeString]:
    """
    Gets the JS items for the base components.
    """
    templates: list[str | SafeString] = []
    if primary_js is None:
        return templates

    # Required to make this function appropriately.
    templates.append(
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
        )
    )

    templates.append(
        mark_safe(
            f"""
<script type="module">
      import {{ initAll }} from "{primary_js}";
      initAll();
    </script>
                    """
        )
    )

    return templates


class PLOSBaseComponent(Component):
    """
    A base component which provides the CSS and JS for all components.
    """

    class Media:
        """
        The media for this component.
        """

        css = get_css()
        js = get_js()
