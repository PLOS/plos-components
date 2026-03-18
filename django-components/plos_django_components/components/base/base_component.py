from django_components import Component


class PLOSBaseComponent(Component):
    class Media:
        css = [
            "https://ux.plos.org/assets/v3/styles/gov-uk-frontend-v6.min.css",
            "https://ux.plos.org/assets/v3/styles/plos-overrides.min.css",
        ]
        js = ["https://ux.plos.org/assets/v3/scripts/gov-uk-frontend-v6.min.js"]
