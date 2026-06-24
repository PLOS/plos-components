import pytest
from django.template import Context, Template
from plos_django_components.components.components.icon.icon import Icon


def test_icon_render_with_icon_name():
    """
    Test rendering using an icon name.
    """
    template = Template(
        '{% load component_tags %}{% component "plos_icon" icon_name="check_circle" %}{% endcomponent %}'
    )
    rendered = template.render(Context({}))
    # Check that it rendered correctly. The icon_base component adds "plos-icon" class.
    assert "plos-icon" in rendered
    # Check that it contains the icon class from bootstrap (e.g., bi-check-circle)
    # The actual class depends on bootstrap definition.
    # In bootstrap_defaults.py, check_circle is "bi bi-check-circle-fill"
    assert "bi bi-check-circle-fill" in rendered


def test_icon_render_with_custom_icon():
    """
    Test rendering using a direct icon class.
    """
    template = Template(
        '{% load component_tags %}{% component "plos_icon" custom_icon="my-custom-icon" %}{% endcomponent %}'
    )
    rendered = template.render(Context({}))
    assert "plos-icon" in rendered
    assert "my-custom-icon" in rendered


def test_icon_missing_args():
    """
    Test that it raises an error when neither icon_name nor custom_icon is provided.
    """
    component = Icon()
    with pytest.raises(ValueError, match="Either 'icon_name' or 'custom_icon' must be provided."):
        component.get_context_data()


def test_icon_render_with_size_and_display():
    """
    Test size and display parameters.
    """
    template = Template(
        "{% load component_tags %}"
        '{% component "plos_icon" custom_icon="my-icon" size="lg" display="block" %}'
        "{% endcomponent %}"
    )
    rendered = template.render(Context({}))
    assert "plos-icon--block" in rendered
    assert 'style="width: 32px; height: 32px;"' in rendered
    assert "my-icon" in rendered


def test_icon_render_with_field_id():
    """
    Test rendering with field_id parameter.
    """
    template = Template(
        "{% load component_tags %}"
        '{% component "plos_icon" custom_icon="my-icon" field_id="test-icon-id" %}'
        "{% endcomponent %}"
    )
    rendered = template.render(Context({}))
    assert 'id="test-icon-id"' in rendered
    assert "my-icon" in rendered


def test_icon_render_with_all_preset_names():
    """
    Test rendering with all available preset icon names.
    """
    preset_icons = {
        "check_circle": "bi bi-check-circle-fill",
        "exclamation_circle": "bi bi-exclamation-circle-fill",
        "info_circle": "bi bi-info-circle-fill",
        "add_item": "bi bi-plus-lg",
        "delete_item": "bi bi-trash3",
        "chevron_down": "bi bi-chevron-down",
    }

    for icon_name, expected_class in preset_icons.items():
        template = Template(
            f'{{% load component_tags %}}{{% component "plos_icon" icon_name="{icon_name}" %}}{{% endcomponent %}}'
        )
        rendered = template.render(Context({}))
        assert "plos-icon" in rendered
        assert expected_class in rendered


def test_icon_render_with_all_sizes():
    """
    Test rendering with all available size options.
    """
    sizes = {
        "xs": 16,
        "sm": 20,
        "md": 24,
        "lg": 32,
        "xl": 40,
    }

    for size, expected_px in sizes.items():
        template = Template(
            f"{{% load component_tags %}}"
            f'{{% component "plos_icon" custom_icon="my-icon" size="{size}" %}}'
            f"{{% endcomponent %}}"
        )
        rendered = template.render(Context({}))
        assert "plos-icon" in rendered
        assert f'style="width: {expected_px}px; height: {expected_px}px;"' in rendered


def test_icon_render_with_display_options():
    """
    Test rendering with different display options.
    """
    template_inline = Template(
        '{% load component_tags %}{% component "plos_icon" custom_icon="my-icon" display="inline" %}{% endcomponent %}'
    )
    rendered_inline = template_inline.render(Context({}))
    assert "plos-icon--inline" in rendered_inline
    assert "plos-icon--block" not in rendered_inline

    template_block = Template(
        '{% load component_tags %}{% component "plos_icon" custom_icon="my-icon" display="block" %}{% endcomponent %}'
    )
    rendered_block = template_block.render(Context({}))
    assert "plos-icon--block" in rendered_block
    assert "plos-icon--inline" not in rendered_block


def test_icon_invalid_size():
    """
    Test that it raises an error when an invalid size is provided.
    """
    component = Icon()
    with pytest.raises(ValueError, match="Invalid icon size 'invalid_size': must be one of xs, sm, md, lg, xl"):
        component.get_context_data(custom_icon="my-icon", size="invalid_size")


def test_icon_invalid_display():
    """
    Test that it raises an error when an invalid display is provided.
    """
    component = Icon()
    with pytest.raises(ValueError, match="Invalid icon display 'invalid_display': must be one of inline, block"):
        component.get_context_data(custom_icon="my-icon", display="invalid_display")


def test_icon_name_precedence():
    """
    Test that icon_name takes precedence over custom_icon when both are provided.
    """
    template = Template(
        "{% load component_tags %}"
        '{% component "plos_icon" icon_name="check_circle" custom_icon="my-custom-icon" %}'
        "{% endcomponent %}"
    )
    rendered = template.render(Context({}))
    # Should use the icon_name value (check_circle -> bi bi-check-circle-fill)
    assert "bi bi-check-circle-fill" in rendered
    # Should not contain the custom_icon value
    assert "my-custom-icon" not in rendered
