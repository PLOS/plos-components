# Icon Component

The Icon component renders icons from icon fonts (like Bootstrap Icons) in a consistent and accessible way.

## Features

- **Preset Icons**: Use predefined icon names for common icons
- **Custom Icons**: Specify custom icon classes from any icon font
- **Sizing**: Multiple predefined sizes (xs, sm, md, lg, xl)
- **Display Options**: Inline or block display modes
- **Accessibility**: Icons are marked as decorative by default with `aria-hidden="true"`
- **Custom IDs**: Add custom IDs for targeting specific icons

## Usage

### Basic Usage

```django
{% load component_tags %}

<!-- Using a preset icon -->
{% component "plos_icon" icon_name="check_circle" %}{% endcomponent %}

<!-- Using a custom icon -->
{% component "plos_icon" custom_icon="bi bi-heart-fill" %}{% endcomponent %}
```

### Icon Sizes

```django
{% component "plos_icon" icon_name="add_item" size="xs" %}{% endcomponent %} <!-- 16px -->
{% component "plos_icon" icon_name="add_item" size="sm" %}{% endcomponent %} <!-- 20px -->
{% component "plos_icon" icon_name="add_item" size="md" %}{% endcomponent %} <!-- 24px (default) -->
{% component "plos_icon" icon_name="add_item" size="lg" %}{% endcomponent %} <!-- 32px -->
{% component "plos_icon" icon_name="add_item" size="xl" %}{% endcomponent %} <!-- 40px -->
```

### Display Options

```django
<!-- Inline (default) - sits alongside other content -->
{% component "plos_icon" icon_name="chevron_down" display="inline" %}{% endcomponent %}

<!-- Block - sits on its own line -->
{% component "plos_icon" icon_name="chevron_down" display="block" %}{% endcomponent %}
```

### With Custom ID

```django
{% component "plos_icon" icon_name="delete_item" field_id="delete-icon-1" %}{% endcomponent %}
```

## Preset Icons

The following preset icons are available:

- `check_circle` - A checkmark inside a circle
- `exclamation_circle` - An exclamation mark inside a circle
- `info_circle` - An information icon inside a circle
- `add_item` - A plus sign for adding items
- `delete_item` - A trash can for deleting items
- `chevron_down` - A downward-pointing chevron

## Customization

### Using Custom Icons

You can use any icon from any icon font by specifying the full CSS class:

```django
{% component "plos_icon" custom_icon="fas fa-user" %}{% endcomponent %}
{% component "plos_icon" custom_icon="bi bi-star-fill" %}{% endcomponent %}
```

### Icon Font Configuration

By default, the component uses Bootstrap Icons. You can change this by setting the `ICON_FONT` in your Django settings:

```python
# settings.py
ICON_FONT = "bootstrap"  # or your custom font identifier
```

### Overriding Icon Classes

You can override the default icon classes by providing an `ICON_FONT_OVERRIDE_DICTIONARY` in your Django settings:

```python
# settings.py
from plos_django_components.components.components.base.icon_fonts.abstract_icon_font_defaults import IconFontDictionary

ICON_FONT_OVERRIDE_DICTIONARY: IconFontDictionary = dict(
    icon_font_url="https://your-cdn.com/custom-icons.css",
    check_circle="custom-custom-check",
    # Override any other icons as needed
)
```

## Accessibility

Icons are rendered with `aria-hidden="true"` by default, making them decorative. For meaningful icons that convey information, provide alternative text in the parent context or use an `aria-label` on a parent element.

## Technical Details

### Component Class

The component is implemented in `icon.py` and uses the template `icon.html`.

### CSS Classes

- `.plos-icon` - Base icon wrapper class
- `.plos-icon--inline` - For inline display (default)
- `.plos-icon--block` - For block display

### Error Handling

The component validates:
- Either `icon_name` or `custom_icon` must be provided
- `size` must be one of the predefined sizes
- `display` must be either "inline" or "block"
