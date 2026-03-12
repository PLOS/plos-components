# PLOS Components

This is a collection of components for [django-components](https://github.com/EmilStenstrom/django-components).

## Installation

```bash
pip install plos-django-components
```

## Setup

Add `plos_django_components` and `django_components` to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    ...,
    "django_components",
    "plos_django_components",
    ...,
]
```

Ensure `django_components.template_loader.Loader` is in your `TEMPLATES` loaders.

## Usage

This package provides components that can be used in your Django templates.
See the `templates/` directory for available components.