"""
Tests for the plos_add_more view helpers in `patterns/add_more/logic.py`.
"""

import pytest
from django.http import QueryDict
from hypothesis import given
from hypothesis import strategies as st
from plos_django_components.components.patterns.add_more.logic import (
    apply_add_or_delete,
    collapsed_after_add_or_delete,
    deleted_index,
    error_summary_entries,
    posted_count,
)


def post(**fields) -> QueryDict:
    query = QueryDict(mutable=True)
    query.update(fields)
    return query


@pytest.mark.parametrize(
    "fields, expected",
    [
        ({"patents__count": "3"}, 3),
        ({}, 1),
        ({"patents__count": ""}, 1),
        ({"patents__count": "abc"}, 1),
        ({"patents__count": "0"}, 1),
        ({"patents__count": "-5"}, 1),
        ({"patents__count": "999999"}, 10),
    ],
)
def test_posted_count(fields, expected):
    assert posted_count(post(**fields), "patents", 10) == expected


@given(st.text())
def test_posted_count_stays_between_one_and_max_items(value):
    assert 1 <= posted_count(post(patents__count=value), "patents", 10) <= 10


@pytest.mark.parametrize(
    "action, expected",
    [
        ("delete__0", 0),
        ("delete__12", 12),
        ("delete__-1", None),
        ("delete__abc", None),
        ("delete__", None),
        ("add", None),
        ("", None),
    ],
)
def test_deleted_index(action, expected):
    assert deleted_index(action) == expected


@pytest.mark.parametrize(
    "values, action, expected",
    [
        (["a"], "add", ["a", ""]),
        (["a", "b"], "add", ["a", "b"]),  # already at max_items
        (["a", "b"], "delete__0", ["b"]),
        (["a", "b"], "delete__1", ["a"]),
        (["a", "b"], "delete__5", ["a", "b"]),  # no such item
        (["a"], "delete__0", [""]),  # never empty
        (["a", "b"], "delete__-1", ["a", "b"]),
        (["a", "b"], "", ["a", "b"]),
        (["a", "b"], "unknown", ["a", "b"]),
    ],
)
def test_apply_add_or_delete(values, action, expected):
    assert apply_add_or_delete(values, action, max_items=2) == expected


def test_apply_add_or_delete_uses_empty_item():
    empty = {"name": "", "role": ""}
    assert apply_add_or_delete([{"name": "a", "role": "b"}], "add", 5, empty_item=empty) == [
        {"name": "a", "role": "b"},
        empty,
    ]
    assert apply_add_or_delete([{"name": "a", "role": "b"}], "delete__0", 5, empty_item=empty) == [empty]


def test_apply_add_or_delete_does_not_change_the_input():
    values = ["a", "b"]
    apply_add_or_delete(values, "delete__0", 5)
    assert values == ["a", "b"]


@pytest.mark.parametrize(
    "collapsed, action, expected",
    [
        ("0,2", "add", [0, 2]),
        ("0,2", "", [0, 2]),
        ("0,2,3", "delete__2", [0, 2]),  # 2 removed, 3 moves up to 2
        ("1,3", "delete__0", [0, 2]),
        ("0,1", "delete__5", [0, 1]),
        ("", "add", []),
        ("0,x", "add", []),
    ],
)
def test_collapsed_after_add_or_delete(collapsed, action, expected):
    assert collapsed_after_add_or_delete(post(patents__collapsed=collapsed), "patents", action) == expected


def test_collapsed_after_add_or_delete_without_the_field():
    assert collapsed_after_add_or_delete(post(), "patents", "add") == []


def test_error_summary_entries():
    errors = [
        None,
        [
            {"field_id": "patent", "message": "Enter a patent number"},
            {"field_id": "country", "message": "Select a country"},
        ],
    ]
    assert error_summary_entries(errors, "patent") == [
        {"label": "Patent 2", "message": "Enter a patent number", "anchor": "patent_1"},
        {"label": "Patent 2", "message": "Select a country", "anchor": "country_1"},
    ]


@pytest.mark.parametrize("errors", [None, [], [None, None]])
def test_error_summary_entries_without_errors(errors):
    assert error_summary_entries(errors, "patent") == []
