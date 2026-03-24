# PLOS Components

This is a collection of components for [django-components](https://github.com/EmilStenstrom/django-components).

## Installation

Currently the best way to use PLOS Components in your Django application is by checking out this repo as a submodule in the top-level path of your project. You can see a working example in the [PLOS Components Showcase repository](https://gitlab.com/plos/plos-components-showcase).

## Setup

This section provides guidance on setting up a generic Django Application and Janeway. 

### Django applications

You will need to make the changes described below to the `settings.py` file of your Django site.

If you’re using the components as a submodule (see [Installation](#Installation) above), add `plos-components` to the Python path:
```python
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / 'plos-components' / 'django-components'))
```

Add the components to the collection of Django apps enabled in your site:
```python
INSTALLED_APPS = [
    ...,
    'django_components',
    'plos_django_components',
    ...,
]
```

Add `'django_components.templatetags.component_tags'` to your `builtins`, and ensure `django_components.template_loader.Loader` is in your `TEMPLATES` loaders as follows:
```python
TEMPLATES = [
        {
            'OPTIONS':
                {
                    'builtins': [
                        'django_components.templatetags.component_tags',
                    ],
                    'loaders': (
                        'django.template.loaders.cached.Loader', [
                        'django.template.loaders.filesystem.Loader',
                        'django.template.loaders.app_directories.Loader',
                        'django_components.template_loader.Loader',
                    ])
                }
        }
    ]
```

Make sure that `'APP_DIRS': True` has been removed, since `APP_DIRS` is incompatible with `loaders`.

### Janeway

This project was originally designed for use with [Janeway Systems](https://github.com/openlibhums/janeway), an open-source publication system. 

When using with Janeway, add the following to your `settings.py`:

```python
import core.janeway_global_settings as global_settings

global_settings.INSTALLED_APPS.append('django_components')
global_settings.INSTALLED_APPS.append('plos_django_components')

global_settings.TEMPLATES[0]['OPTIONS']['loaders'].append((
    'django.template.loaders.cached.Loader', [
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django_components.template_loader.Loader',
]))

global_settings.TEMPLATES[0]['OPTIONS']['builtins'].append((
    'django_components.templatetags.component_tags',
]))
```

## Usage

This package provides components that can be used in your Django templates.
See the `plos_django_components/components` directory for available components.

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
