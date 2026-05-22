# design_system

A lightweight Django application for browsing PLOS design system styles and components. It pulls components from the `django-components/plos-django-components` package and renders live examples alongside documentation.

## Structure

This directory is a Django project root. It contains two subdirectories that serve different roles:

```txt
design_system/
├── design_system/   Django project config (settings, root URLs, WSGI)
├── showcase/        Django app (all views, templates, and static files)
├── manage.py        Django management script
└── pyproject.toml   Project metadata and dependencies
```

`design_system/` and `showcase/` are sibling directories because Django separates the project config package from application packages. The config package (`design_system/`) holds settings and wires everything together; the app (`showcase/`) contains all the code that actually runs. See their individual READMEs for details:

- [design_system/README.md](design_system/README.md) — project config package
- [showcase/README.md](showcase/README.md) — showcase app

## Setup

From the repo root (`plos-components`), run once to apply database migrations (required for session storage):

```bash
uv run python design_system/manage.py migrate
```

Then start the development server:

```bash
uv run python design_system/manage.py runserver
```

The app will be available at `http://localhost:8000/`.

## Dependencies

- Python >= 3.10
- Django >= 4.2
- `plos-django-components` (workspace dependency from `django-components/`)
