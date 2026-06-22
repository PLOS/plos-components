"""
Tests for the TextInput component.

This module contains unit tests and property-based tests using Hypothesis to verify
the logic and rendering of the plos_text_input component.
"""
import pytest
from django.template import Context, Template
from hypothesis import given
from hypothesis import strategies as st
from plos_django_components.components.components.text_input.text_input import TextInput
from plos_django_components.utils.govuk_helper import label_class_from_size


@pytest.mark.parametrize(
    "input_type, expected_step",
    [
        ("text", None),
        ("number", "any"),
        ("password", None),
        ("email", None),
        ("url", None),
    ],
)
def test_text_input_step_logic(input_type, expected_step):
    """
    Test that the 'step' attribute is correctly set based on the 'input_type'.
    Specifically, 'number' type should default to 'any'.
    """
    component = TextInput()
    context = component.get_context_data(label="Label", name="name", input_type=input_type)
    assert context["step"] == expected_step


def test_text_input_custom_step():
    """
    Test that a custom 'step' value is preserved for 'number' inputs.
    """
    component = TextInput()
    context = component.get_context_data(label="Label", name="name", input_type="number", step="0.01")
    assert context["step"] == "0.01"


@given(
    label=st.text(min_size=1),
    name=st.text(min_size=1, alphabet=st.characters(blacklist_categories=["Cc", "Cs"])),
    label_size=st.sampled_from(["large", "medium", "small"]),
    value=st.text(),
    required=st.booleans(),
)
def test_text_input_context_generation(label, name, label_size, value, required):
    """
    Use Hypothesis to test that get_context_data correctly processes various inputs.
    """
    component = TextInput()
    context = component.get_context_data(label=label, name=name, label_size=label_size, value=value, required=required)
    assert context["label"] == label
    assert context["name"] == name
    assert context["value"] == value
    assert context["required"] == required
    assert context["id"] == f"id_{name}"

    expected_label_class = label_class_from_size(label_size)
    assert context["label_class"] == expected_label_class


def test_text_input_custom_id():
    """
    Test that providing a custom 'field_id' overrides the default ID.
    """
    component = TextInput()
    context = component.get_context_data(label="Label", name="name", field_id="custom-id")
    assert context["id"] == "custom-id"


def test_text_input_render_basic():
    """
    Test basic rendering of the text input component.
    """
    template = Template(
        '{% load component_tags %}{% component "plos_text_input" label="My Label" name="my_name" %}{% endcomponent %}'
    )
    rendered = template.render(Context({}))
    assert "My Label" in rendered
    assert 'name="my_name"' in rendered
    assert 'id="id_my_name"' in rendered
    assert 'class="govuk-label govuk-label--s"' in rendered


def test_text_input_render_with_errors():
    """
    Test rendering of the component when error messages are provided.
    """
    errors = ["Error 1", "Error 2"]
    template = Template(
        '{% load component_tags %}{% component "plos_text_input" label="L" name="n" errors=errors %}{% endcomponent %}'
    )
    rendered = template.render(Context({"errors": errors}))
    assert "govuk-form-group--error" in rendered
    assert "govuk-input--error" in rendered
    assert "Error 1" in rendered
    assert "Error 2" in rendered


def test_text_input_render_with_hint():
    """
    Test rendering of the component with a hint and verify ARIA associations.
    """
    template = Template(
        '{% load component_tags %}{% component "plos_text_input" label="L" name="n" hint="My Hint" %}{% endcomponent %}'
    )
    rendered = template.render(Context({}))
    assert "My Hint" in rendered
    assert 'id="id_n-hint"' in rendered
    assert 'aria-describedby="id_n-hint"' in rendered


def test_text_input_render_with_prefix_suffix():
    """
    Test rendering of the component with prefix and suffix elements.
    """
    template = Template(
        '{% load component_tags %}{% component "plos_text_input" label="L" name="n" prefix="Pre" suffix="Suf" %}'
        "{% endcomponent %}"
    )
    rendered = template.render(Context({}))
    assert "govuk-input__prefix" in rendered
    assert "Pre" in rendered
    assert "govuk-input__suffix" in rendered
    assert "Suf" in rendered


def test_text_input_render_attributes():
    """
    Test that various HTML attributes are correctly rendered in the input tag.
    """
    template = Template(
        "{% load component_tags %}"
        '{% component "plos_text_input" '
        'label="L" name="n" value="val" placeholder="place" '
        "required=True disabled=True maxlength=10 minlength=5 "
        "%}{% endcomponent %}"
    )
    rendered = template.render(Context({}))
    assert 'value="val"' in rendered
    assert 'placeholder="place"' in rendered
    assert "required" in rendered
    assert "disabled" in rendered
    assert "maxlength=10" in rendered
    assert "minlength=5" in rendered
