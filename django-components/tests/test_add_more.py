"""
Tests for the AddMore pattern.

This module contains unit tests and property-based tests using Hypothesis to verify
the logic, session management, and context generation for the plos_add_more component.
"""

from django.core import signing
from django.http import HttpRequest, QueryDict
from hypothesis import given
from hypothesis import settings as hypothesis_settings
from hypothesis import strategies as st
from plos_django_components.components.patterns.add_more.add_more import (
    AddMore,
    any_field_required,
    get_session_key_errors,
    get_session_key_values,
    is_required_field,
)
from plos_django_components.components.patterns.add_more.typed_dict.add_more_fields import AddMoreField
from plos_django_components.components.patterns.add_more.typed_dict.add_more_value import AddMoreValue
from plos_django_components.components.universal_dictionaries.component_error import PLOSComponentError

# --- Strategies ---


@st.composite
def plos_component_error_strategy(draw):
    """
    Hypothesis strategy for generating PLOSComponentError instances.
    """
    return PLOSComponentError(
        label=draw(st.one_of(st.none(), st.text())),
        message=draw(st.one_of(st.none(), st.text())),
        anchor=draw(st.one_of(st.none(), st.text())),
    )


@st.composite
def add_more_field_strategy(draw):
    """
    Hypothesis strategy for generating AddMoreField instances.
    """
    return AddMoreField(
        field_id=draw(st.one_of(st.none(), st.text())),
        field_name=draw(st.one_of(st.none(), st.text())),
        required=draw(st.one_of(st.none(), st.booleans())),
        field_value_names=draw(st.one_of(st.none(), st.lists(st.text()))),
    )


@st.composite
def add_more_value_strategy(draw):
    """
    Hypothesis strategy for generating AddMoreValue instances.
    """
    return AddMoreValue(
        index=draw(st.one_of(st.none(), st.text())),
        is_first=draw(st.one_of(st.none(), st.booleans())),
        errors=draw(st.one_of(st.none(), st.lists(plos_component_error_strategy()))),
        values=draw(st.one_of(st.none(), st.dictionaries(st.text(), st.text()))),
    )


# --- Utility Function Tests ---


@given(st.text())
def test_get_session_key_values(field_name):
    """
    Test that get_session_key_values returns the expected session key for values.
    """
    assert get_session_key_values(field_name) == f"add_more_{field_name}_values"


@given(st.text())
def test_get_session_key_errors(field_name):
    """
    Test that get_session_key_errors returns the expected session key for errors.
    """
    assert get_session_key_errors(field_name) == f"add_more_{field_name}_errors"


@given(st.lists(add_more_field_strategy()))
def test_any_field_required_list(fields):
    """
    Test that any_field_required correctly identifies if any field in a list is required.
    """
    expected = any(f.get("required", False) for f in fields if isinstance(f, dict))
    assert any_field_required(fields) == expected


def test_any_field_required_string():
    """
    Test that any_field_required correctly parses and checks a string representation of fields.
    """
    fields_str = "[{'field_id': 'f1', 'required': True}, {'field_id': 'f2'}]"
    assert any_field_required(fields_str) is True

    fields_str = "[{'field_id': 'f1'}, {'field_id': 'f2'}]"
    assert any_field_required(fields_str) is False

    assert any_field_required("invalid") is False


@given(add_more_field_strategy())
def test_is_required_field(field):
    """
    Test that is_required_field correctly identifies if a single field is required.
    """
    assert is_required_field(field) == field.get("required", False)


# --- Component Logic Tests ---


def create_mock_request(session_data=None):
    """
    Utility to create a mock HttpRequest with optional session data.
    """
    request = HttpRequest()
    request.session = session_data if session_data is not None else {}
    return request


@given(
    field_name=st.text(min_size=1, alphabet=st.characters(blacklist_categories=["Cc", "Cs"])),
    item_label=st.text(),
    min_items=st.integers(min_value=1, max_value=5),
    max_items=st.integers(min_value=6, max_value=10),
)
def test_get_context_data_initialization(field_name, item_label, min_items, max_items):
    """
    Test the initialization of AddMore component context data, including session setup.
    """
    component = AddMore()
    # Mock request to test session initialization
    request = create_mock_request()
    component.request = request

    context = component.get_template_data(
        None,
        AddMore.Kwargs(
            field_name=field_name,
            item_label=item_label,
            fields=[],
            min_items=min_items,
            max_items=max_items,
        ),
        None,
        None,
    )._asdict()

    assert context["field_name"] == field_name
    assert context["item_label"] == item_label
    assert context["count"] == min_items
    assert len(context["add_more_items"]) == min_items
    assert context["show_delete"] is False
    assert context["remaining"] == max_items - min_items

    # Check session persistence
    session_key = get_session_key_values(field_name)
    # The component initializes session values with [{"errors": [], "values": {}}] * min_items
    # if values was None. Actually, looking at add_more.py:
    # values = [{}] * min_items
    # but then in the loop it accesses value["errors"] and value["values"]
    # So my hypothesis was correct that it will fail if they are missing.
    assert request.session[session_key] == [{"errors": [], "values": {}}] * min_items


@given(
    field_name=st.text(min_size=1, alphabet=st.characters(blacklist_categories=["Cc", "Cs"])),
    item_label=st.text(),
    count=st.integers(min_value=2, max_value=10),
)
def test_get_context_data_with_existing_values(field_name, item_label, count):
    """
    Test that get_context_data correctly handles and preserves existing values.
    """
    component = AddMore()
    values = [{"values": {"f1": f"v{i}"}, "errors": []} for i in range(count)]

    component.request = None
    context = component.get_template_data(
        None,
        AddMore.Kwargs(
            field_name=field_name,
            item_label=item_label,
            fields=[],
            values=values,
        ),
        None,
        None,
    )._asdict()

    assert context["count"] == count
    assert len(context["add_more_items"]) == count
    for i in range(count):
        assert context["add_more_items"][i]["index"] == str(i)
        assert context["add_more_items"][i]["values"] == values[i]["values"]
        assert context["add_more_items"][i]["is_first"] == (i == 0)
        assert context["add_more_items"][i]["errors"] == values[i]["errors"]


def test_get_context_data_show_delete():
    """
    Test the logic for showing/hiding the delete button based on current count and min_items.
    """
    component = AddMore()

    # count == min_items
    context = component.get_template_data(
        None,
        AddMore.Kwargs(field_name="f", item_label="L", fields=[], min_items=2, count=2),
        None,
        None,
    )._asdict()
    assert context["show_delete"] is False

    # count > min_items
    context = component.get_template_data(
        None,
        AddMore.Kwargs(field_name="f", item_label="L", fields=[], min_items=2, count=3),
        None,
        None,
    )._asdict()
    assert context["show_delete"] is True


def test_get_context_data_error_summary():
    """
    Test that get_context_data correctly processes and includes error summaries.
    """
    component = AddMore()
    errors = [
        {"label": "Item 1", "message": "Error 1", "anchor": "#a1"},
        {"label": "Item 2", "message": "Error 2", "anchor": "#a2"},
    ]

    context = component.get_template_data(
        None,
        AddMore.Kwargs(field_name="f", item_label="L", fields=[], errors=errors),
        None,
        None,
    )._asdict()
    assert context["error_summary"] == errors
    assert context["has_errors"] is True


def test_get_context_data_session_pop_errors():
    """
    Test that errors are correctly retrieved from the session and then cleared.
    """
    component = AddMore()
    field_name = "test_field"
    session_key_errors = get_session_key_errors(field_name)
    errors = [{"message": "Session Error"}]

    request = create_mock_request({session_key_errors: errors})
    component.request = request

    context = component.get_template_data(
        None,
        AddMore.Kwargs(field_name=field_name, item_label="L", fields=[]),
        None,
        None,
    )._asdict()

    assert context["error_summary"] == errors
    # Errors should be popped from session
    assert session_key_errors not in request.session


# --- View Logic Tests ---


@given(
    field_name=st.text(min_size=1, alphabet=st.characters(blacklist_categories=["Cc", "Cs"])),
    count=st.integers(min_value=1, max_value=9),
    min_items=st.integers(min_value=1, max_value=5),
    max_items=st.integers(min_value=10, max_value=20),
)
@hypothesis_settings(deadline=None)
def test_view_post_add_action(field_name, count, min_items, max_items):
    """
    Test the 'add' action in the AddMore.View POST handler, ensuring item count increases.
    """
    view = AddMore.View(component=AddMore())
    request = create_mock_request()
    request.method = "POST"

    fields = [{"field_id": "f1", "required": True}]

    post_data = QueryDict(mutable=True)
    post_data.update(
        {
            f"{field_name.lower().strip()}__action": "add",
            f"{field_name.lower().strip()}__config": signing.dumps(
                {
                    "fields": fields,
                    "count": count,
                    "min_items": min_items,
                    "max_items": max_items,
                }
            ),
            "f1_0": "val0",
        }
    )
    request.POST = post_data

    response = view.post(request)

    assert response.status_code == 302
    # On 'add', count should increase by 1
    session_key = get_session_key_values(field_name.lower().strip())
    assert len(request.session[session_key]) == count + 1
    # Check that existing values were preserved
    assert request.session[session_key][0]["values"]["f1"] == "val0"


@given(
    field_name=st.text(min_size=1, alphabet=st.characters(blacklist_categories=["Cc", "Cs"])),
    count=st.integers(min_value=2, max_value=10),
    index_to_delete=st.integers(min_value=0, max_value=9),
)
@hypothesis_settings(deadline=None)
def test_view_post_delete_action(field_name, count, index_to_delete):
    """
    Test the 'delete' action in the AddMore.View POST handler, ensuring the correct item is removed.
    """
    # Ensure index_to_delete < count
    index_to_delete = index_to_delete % count

    view = AddMore.View(component=AddMore())
    request = create_mock_request()
    request.method = "POST"

    fields = [{"field_id": "f1"}]

    post_data = QueryDict(mutable=True)
    post_data.update(
        {
            f"{field_name.lower().strip()}__action": f"delete__{index_to_delete}",
            f"{field_name.lower().strip()}__config": signing.dumps(
                {
                    "fields": fields,
                    "count": count,
                    "min_items": 1,
                    "max_items": 20,
                }
            ),
        }
    )
    # Fill with some values
    for i in range(count):
        post_data[f"f1_{i}"] = f"val{i}"

    request.POST = post_data

    response = view.post(request)

    assert response.status_code == 302
    session_key = get_session_key_values(field_name.lower().strip())
    assert len(request.session[session_key]) == count - 1
    # Check that the correct item was deleted
    values = [v["values"].get("f1") for v in request.session[session_key]]
    assert f"val{index_to_delete}" not in values


def test_view_post_missing_action():
    """
    Test that the AddMore.View POST handler returns a 400 error when the action is missing.
    """
    view = AddMore.View(component=AddMore())
    request = create_mock_request()
    request.method = "POST"
    request.POST = QueryDict("something=else")

    response = view.post(request)
    assert response.status_code == 400
    assert response.content == b"Missing action name"
