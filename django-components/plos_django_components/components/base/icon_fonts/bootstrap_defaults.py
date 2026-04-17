"""
Public settings for default bootstrap.
"""


def bootstrap() -> dict[str, str]:
    """
    Gets the default icon font settings for the Bootstrap icon font.

    :return: A dictionary with the default icon font settings.
    """
    return {
        "ICON_FONT_URL": "https://cdnjs.cloudflare.com/ajax/libs/bootstrap-icons/1.13.1/font/bootstrap-icons.min.css",
        "ICON_FONT_INTEGRITY": "sha512-t7Few9xlddEmgd3oKZQahkNI4dS6l80+eGEzFQiqtyVYdvcSG2D3Iub77R20BdotfRPA9caaRkg1tyaJiPmO0g==",
        "CHECK_CIRCLE": "bi bi-check-circle-fill",
        "INFO_CIRCLE": "bi bi-info-circle-fill",
        "EXCLAMATION_CIRCLE": "bi bi-exclamation-circle-fill",
    }
