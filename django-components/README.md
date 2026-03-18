# PLOS Components

This is a collection of components for [django-components](https://github.com/EmilStenstrom/django-components).

## Installation

This area is under construction!

## Setup

The following provides guidance on setting up a generic Django Application and Janeway. 

### General Setup

Add `plos_django_components` and `django_components` to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    ...,
    "django_components",
    "plos_django_components",
    ...,
]
```

Ensure `django_components.template_loader.Loader` is in your `TEMPLATES` loaders as follows (remove `'APP_DIRS': True`):

```python
TEMPLATES = [
        {
            "OPTIONS":
                {
                    "loaders": (
                        'django.template.loaders.cached.Loader', [
                        'django.template.loaders.filesystem.Loader',
                        'django.template.loaders.app_directories.Loader',
                        'django_components.template_loader.Loader',
                    ])
                }
        }
    ]
```

### Janeway

This project was originally designed for use with [Janeway Systems](https://github.com/openlibhums/janeway), an open-source publication system. 

When using with Janeway, add the following to your `settings.py`:

```python
import core.janeway_global_settings as global_settings

global_settings.INSTALLED_APPS.append('django_components')
global_settings.INSTALLED_APPS.append('plos_django_components')

global_settings.TEMPLATES[0]["OPTIONS"]["loaders"].append((
    'django.template.loaders.cached.Loader', [
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django_components.template_loader.Loader',
]))
```

## Usage

This package provides components that can be used in your Django templates.
See the `templates/` directory for available components.

### Button

The following demonstrates an example using the `Button` component. 

```python
from django.shortcuts import render

def button_example(request):
    template = "example.html"
    context = {}

    return render(request, template, context)
```

Then the HTML file will be as follows:

```html
{% load component_tags %}

<div>
    {% component "plos_button" %}
    Next
    {% endcomponent %}
</div>
```

This will render a simple button which says "Next". 
