"""
Tests for the DateInput component.

This module contains unit tests and property-based tests using Hypothesis to verify
the logic of the plos_date_input component's static methods.
"""

from datetime import date

from hypothesis import given
from hypothesis import strategies as st
from plos_django_components.components.components.date_input.date_input import (
    DateInput,
    DateSettingOption,
    DateSettings,
    DateValue,
)


class TestDateInput:
    """Test cases for DateInput static methods."""

    # Tests for create_default_field_id
    @given(st.text(), st.sampled_from(["day", "month", "year"]))
    def test_create_default_field_id(self, field_id, date_item):
        """Test that create_default_field_id correctly formats the field ID."""
        result = DateInput.create_default_field_id(field_id, date_item)
        expected = f"{field_id}-{date_item}"
        assert result == expected

    # Tests for create_default_field_name
    @given(st.text(), st.sampled_from(["day", "month", "year"]))
    def test_create_default_field_name(self, field_name, date_item):
        """Test that create_default_field_name correctly formats the field name."""
        result = DateInput.create_default_field_name(field_name, date_item)
        expected = f"{field_name}-{date_item}"
        assert result == expected

    # Tests for merge_setting_option
    @given(
        st.one_of(st.none(), st.dictionaries(st.text(), st.one_of(st.text(), st.none(), st.booleans()))),
        st.booleans(),
        st.text(),
        st.one_of(st.none(), st.text()),
        st.text(),
        st.sampled_from(["day", "month", "year"]),
    )
    def test_merge_setting_option(
        self, setting, display, default_field_id, default_field_name, default_label, date_item
    ):
        """Test that merge_setting_option correctly merges settings."""
        result = DateInput.merge_setting_option(
            setting, display, default_field_id, default_field_name, default_label, date_item
        )

        # Check that display is set correctly
        if setting and setting.get("display") is not None:
            assert result["display"] == setting["display"]
        else:
            assert result["display"] == display

        # Check that field_id is set correctly
        if setting and setting.get("field_id") is not None:
            assert result["field_id"] == setting["field_id"]
        else:
            assert result["field_id"] == f"{default_field_id}-{date_item}"

        # Check that field_name is set correctly
        if setting and setting.get("field_name") is not None:
            assert result["field_name"] == setting["field_name"]
        else:
            expected_field_name = default_field_name if default_field_name is not None else default_field_id
            assert result["field_name"] == f"{expected_field_name}-{date_item}"

        # Check that label is set correctly
        # Note: The method only sets label when setting is None, not when it's missing the label key
        if setting is None:
            assert result["label"] == default_label
        elif "label" in setting and setting["label"] is not None:
            assert result["label"] == setting["label"]
        # If setting exists but doesn't have a label key, the method doesn't set it

    # Property-based tests for merge_setting_option
    @given(st.text(), st.text(), st.booleans(), st.one_of(st.none(), st.text()))
    def test_merge_setting_option_property_based(self, default_field_id, default_label, display, default_field_name):
        """Property-based test for merge_setting_option with various parameters."""
        # Test with None setting
        result = DateInput.merge_setting_option(
            None, display, default_field_id, default_field_name, default_label, "day"
        )
        assert result["display"] == display
        assert result["label"] == default_label
        assert result["field_id"] == f"{default_field_id}-day"
        expected_field_name = default_field_name if default_field_name is not None else default_field_id
        assert result["field_name"] == f"{expected_field_name}-day"

    # Tests for merge_settings
    @given(
        st.one_of(st.none(), st.builds(DateSettings)),
        st.text(),
        st.one_of(st.none(), st.text()),
        st.booleans(),
        st.booleans(),
        st.booleans(),
    )
    def test_merge_settings(self, settings, default_field_id, default_field_name, day, month, year):
        """Test that merge_settings correctly merges all settings."""
        result = DateInput.merge_settings(settings, default_field_id, default_field_name, day, month, year)

        # Check that all three date components are present
        assert "day" in result
        assert "month" in result
        assert "year" in result

        # Check that each component is properly merged
        # Day
        if settings and settings.get("day") is not None:
            setting = settings["day"]
            if setting.get("display") is not None:
                assert result["day"]["display"] == setting["display"]
            else:
                assert result["day"]["display"] == day

            if setting.get("field_id") is not None:
                assert result["day"]["field_id"] == setting["field_id"]
            else:
                assert result["day"]["field_id"] == f"{default_field_id}-day"

            if setting.get("field_name") is not None:
                assert result["day"]["field_name"] == setting["field_name"]
            else:
                expected_field_name = default_field_name if default_field_name is not None else default_field_id
                assert result["day"]["field_name"] == f"{expected_field_name}-day"
        else:
            assert result["day"]["display"] == day
            assert result["day"]["field_id"] == f"{default_field_id}-day"
            expected_field_name = default_field_name if default_field_name is not None else default_field_id
            assert result["day"]["field_name"] == f"{expected_field_name}-day"

        # Month
        if settings and settings.get("month") is not None:
            setting = settings["month"]
            if setting.get("display") is not None:
                assert result["month"]["display"] == setting["display"]
            else:
                assert result["month"]["display"] == month

            if setting.get("field_id") is not None:
                assert result["month"]["field_id"] == setting["field_id"]
            else:
                assert result["month"]["field_id"] == f"{default_field_id}-month"

            if setting.get("field_name") is not None:
                assert result["month"]["field_name"] == setting["field_name"]
            else:
                expected_field_name = default_field_name if default_field_name is not None else default_field_id
                assert result["month"]["field_name"] == f"{expected_field_name}-month"
        else:
            assert result["month"]["display"] == month
            assert result["month"]["field_id"] == f"{default_field_id}-month"
            expected_field_name = default_field_name if default_field_name is not None else default_field_id
            assert result["month"]["field_name"] == f"{expected_field_name}-month"

        # Year
        if settings and settings.get("year") is not None:
            setting = settings["year"]
            if setting.get("display") is not None:
                assert result["year"]["display"] == setting["display"]
            else:
                assert result["year"]["display"] == year

            if setting.get("field_id") is not None:
                assert result["year"]["field_id"] == setting["field_id"]
            else:
                assert result["year"]["field_id"] == f"{default_field_id}-year"

            if setting.get("field_name") is not None:
                assert result["year"]["field_name"] == setting["field_name"]
            else:
                expected_field_name = default_field_name if default_field_name is not None else default_field_id
                assert result["year"]["field_name"] == f"{expected_field_name}-year"
        else:
            assert result["year"]["display"] == year
            assert result["year"]["field_id"] == f"{default_field_id}-year"
            expected_field_name = default_field_name if default_field_name is not None else default_field_id
            assert result["year"]["field_name"] == f"{expected_field_name}-year"

    # Property-based tests for merge_settings with various parameters
    @given(st.text(), st.one_of(st.none(), st.text()), st.booleans(), st.booleans(), st.booleans())
    def test_merge_settings_property_based(self, default_field_id, default_field_name, day, month, year):
        """Property-based test for merge_settings with various parameters."""
        # Skip empty default_field_id as it would create invalid field IDs
        if not default_field_id:
            return

        result = DateInput.merge_settings(None, default_field_id, default_field_name, day, month, year)

        # Check that all three date components are present
        assert "day" in result
        assert "month" in result
        assert "year" in result

        # Check that each component has the correct display value
        assert result["day"]["display"] == day
        assert result["month"]["display"] == month
        assert result["year"]["display"] == year

        # Check that each component has the correct field_id
        assert result["day"]["field_id"] == f"{default_field_id}-day"
        assert result["month"]["field_id"] == f"{default_field_id}-month"
        assert result["year"]["field_id"] == f"{default_field_id}-year"

        # Check that each component has the correct field_name
        expected_field_name = default_field_name if default_field_name is not None else default_field_id
        assert result["day"]["field_name"] == f"{expected_field_name}-day"
        assert result["month"]["field_name"] == f"{expected_field_name}-month"
        assert result["year"]["field_name"] == f"{expected_field_name}-year"

    # Tests for convert_to_date
    @given(st.integers(1, 9999), st.integers(1, 12), st.integers(1, 31))
    def test_convert_to_date_valid(self, year, month, day):
        """Test that convert_to_date correctly converts valid DateValue to date."""
        date_value = DateValue(year=year, month=month, day=day)
        result = DateInput.convert_to_date(date_value)

        # For valid dates, we should get a date object
        if result is not None:
            assert isinstance(result, date)
            assert result.year == year
            assert result.month == month
            assert result.day == day

    def test_convert_to_date_invalid(self):
        """Test that convert_to_date returns a default date for invalid dates."""
        # Test with invalid date (February 30)
        result = DateInput.convert_to_date(DateValue(year=2023, month=2, day=30))
        assert result is not None
        assert isinstance(result, date)
        assert result.year == 1900
        assert result.month == 1
        assert result.day == 1

    # Tests for convert_from_date
    @given(st.dates())
    def test_convert_from_date(self, date_obj):
        """Test that convert_from_date correctly converts date to DateValue."""
        result = DateInput.convert_from_date(date_obj)

        # Check that result is a dict with the expected keys
        assert isinstance(result, dict)
        assert "year" in result
        assert "month" in result
        assert "day" in result

        # Check that the values are correct
        assert result["year"] == date_obj.year
        assert result["month"] == date_obj.month
        assert result["day"] == date_obj.day

    # Additional property-based tests for convert_from_date
    @given(st.integers(1, 9999), st.integers(1, 12), st.integers(1, 31))
    def test_convert_from_date_with_components(self, year, month, day):
        """Test that convert_from_date correctly converts date components."""
        try:
            date_obj = date(year, month, day)
            result = DateInput.convert_from_date(date_obj)
            assert isinstance(result, dict)
            assert result["year"] == year
            assert result["month"] == month
            assert result["day"] == day
        except ValueError:
            # Handle invalid dates like Feb 30
            pass

    # Tests for convert_any_date_value_to_date
    @given(st.dates())
    def test_convert_any_date_value_to_date_with_date_object(self, date_obj):
        """Test that convert_any_date_value_to_date works with date objects."""
        result = DateInput.convert_any_date_value_to_date(date_obj)
        assert isinstance(result, date)
        assert result == date_obj

    def test_convert_any_date_value_to_date_with_datevalue(self):
        """Test that convert_any_date_value_to_date works with DateValue objects."""
        date_value = DateValue(year=2023, month=6, day=15)
        result = DateInput.convert_any_date_value_to_date(date_value)
        assert isinstance(result, date)
        assert result.year == 2023
        assert result.month == 6
        assert result.day == 15

    def test_convert_any_date_value_to_date_with_none(self):
        """Test that convert_any_date_value_to_date works with None."""
        result = DateInput.convert_any_date_value_to_date(None)
        assert isinstance(result, date)
        assert result.year == 1900
        assert result.month == 1
        assert result.day == 1

    def test_convert_any_date_value_to_date_with_blank_out_flags(self):
        """Test that convert_any_date_value_to_date works with blank out flags."""
        # Test with date object and blank_out_day
        date_obj = date(2023, 6, 15)
        result = DateInput.convert_any_date_value_to_date(date_obj, blank_out_day=True)
        assert isinstance(result, date)
        assert result.year == 2023
        assert result.month == 6
        assert result.day == 1  # Default day

        # Test with date object and blank_out_month
        result = DateInput.convert_any_date_value_to_date(date_obj, blank_out_month=True)
        assert isinstance(result, date)
        assert result.year == 2023
        assert result.month == 1  # Default month
        assert result.day == 15

        # Test with date object and blank_out_year
        result = DateInput.convert_any_date_value_to_date(date_obj, blank_out_year=True)
        assert isinstance(result, date)
        assert result.year == 1900  # Default year
        assert result.month == 6
        assert result.day == 15

        # Test with DateValue and blank_out_day
        date_value = DateValue(year=2023, month=6, day=15)
        result = DateInput.convert_any_date_value_to_date(date_value, blank_out_day=True)
        assert isinstance(result, date)
        assert result.year == 2023
        assert result.month == 6
        assert result.day == 1  # Default day

        # Test with DateValue and blank_out_month
        result = DateInput.convert_any_date_value_to_date(date_value, blank_out_month=True)
        assert isinstance(result, date)
        assert result.year == 2023
        assert result.month == 1  # Default month
        assert result.day == 15

        # Test with DateValue and blank_out_year
        result = DateInput.convert_any_date_value_to_date(date_value, blank_out_year=True)
        assert isinstance(result, date)
        assert result.year == 1900  # Default year
        assert result.month == 6
        assert result.day == 15

    # Property-based tests for convert_any_date_value_to_date
    @given(st.integers(1, 9999), st.integers(1, 12), st.integers(1, 31))
    def test_convert_any_date_value_to_date_with_datevalue_components(self, year, month, day):
        """Test that convert_any_date_value_to_date works with DateValue components."""
        date_value = DateValue(year=year, month=month, day=day)
        result = DateInput.convert_any_date_value_to_date(date_value)
        assert isinstance(result, date)
        # Handle potential invalid dates
        try:
            expected = date(year, month, day)
            assert result == expected
        except ValueError:
            # For invalid dates, should return default date
            assert result.year == 1900
            assert result.month == 1
            assert result.day == 1

    # Additional tests for failure states and edge cases

    def test_convert_to_date_with_empty_dict(self):
        """Test that convert_to_date returns a default date when passed an empty DateValue."""
        result = DateInput.convert_to_date(DateValue())
        assert result is not None
        assert isinstance(result, date)
        assert result.year == 1900
        assert result.month == 1
        assert result.day == 1

    def test_convert_to_date_with_missing_components(self):
        """Test that convert_to_date works with partial dates using default values."""
        # Test with only year
        result = DateInput.convert_to_date(DateValue(year=2023))
        assert result is not None
        assert isinstance(result, date)
        assert result.year == 2023
        assert result.month == 1  # Default month
        assert result.day == 1  # Default day

        # Test with only month
        result = DateInput.convert_to_date(DateValue(month=6))
        assert result is not None
        assert isinstance(result, date)
        assert result.year == 1900  # Default year
        assert result.month == 6
        assert result.day == 1  # Default day

        # Test with only day
        result = DateInput.convert_to_date(DateValue(day=15))
        assert result is not None
        assert isinstance(result, date)
        assert result.year == 1900  # Default year
        assert result.month == 1  # Default month
        assert result.day == 15

        # Test with year and month
        result = DateInput.convert_to_date(DateValue(year=2023, month=6))
        assert result is not None
        assert isinstance(result, date)
        assert result.year == 2023
        assert result.month == 6
        assert result.day == 1  # Default day

        # Test with year and day
        result = DateInput.convert_to_date(DateValue(year=2023, day=15))
        assert result is not None
        assert isinstance(result, date)
        assert result.year == 2023
        assert result.month == 1  # Default month
        assert result.day == 15

        # Test with month and day
        result = DateInput.convert_to_date(DateValue(month=6, day=15))
        assert result is not None
        assert isinstance(result, date)
        assert result.year == 1900  # Default year
        assert result.month == 6
        assert result.day == 15

        # Test with all components (complete date)
        result = DateInput.convert_to_date(DateValue(year=2023, month=6, day=15))
        assert result is not None
        assert isinstance(result, date)
        assert result.year == 2023
        assert result.month == 6
        assert result.day == 15

    def test_merge_settings_with_none_values(self):
        """Test that merge_settings correctly handles None values."""
        result = DateInput.merge_settings(None, "test-id", "test-name", True, True, True)
        assert "day" in result
        assert "month" in result
        assert "year" in result
        assert result["day"]["display"] is True
        assert result["month"]["display"] is True
        assert result["year"]["display"] is True

    def test_create_default_field_id_with_empty_strings(self):
        """Test that create_default_field_id handles empty strings."""
        result = DateInput.create_default_field_id("", "day")
        assert result == "-day"

    def test_create_default_field_name_with_empty_strings(self):
        """Test that create_default_field_name handles empty strings."""
        result = DateInput.create_default_field_name("", "day")
        assert result == "-day"

    def test_merge_setting_option_with_none_setting(self):
        """Test that merge_setting_option correctly handles None setting."""
        result = DateInput.merge_setting_option(None, True, "test-id", "test-name", "Day", "day")
        assert result["display"] is True
        assert result["label"] == "Day"
        assert result["field_id"] == "test-id-day"
        assert result["field_name"] == "test-name-day"

    # Tests for is_date_before_or_equal
    @given(st.dates(), st.dates())
    def test_is_date_before_or_equal_with_date_objects(self, first_date, second_date):
        """Test that is_date_before_or_equal works correctly with date objects."""
        result = DateInput.is_date_before_or_equal(first_date, second_date)
        expected = first_date <= second_date
        assert result == expected

    def test_is_date_before_or_equal_with_same_dates(self):
        """Test that is_date_before_or_equal returns True for identical dates."""
        test_date = date(2023, 6, 15)
        result = DateInput.is_date_before_or_equal(test_date, test_date)
        assert result is True

    def test_is_date_before_or_equal_with_date_and_datevalue(self):
        """Test that is_date_before_or_equal works with mixed date and DateValue inputs."""
        test_date = date(2023, 6, 15)
        date_value = DateValue(year=2023, month=6, day=20)

        # date <= DateValue
        result1 = DateInput.is_date_before_or_equal(test_date, date_value)
        assert result1 is True

        # DateValue <= date
        result2 = DateInput.is_date_before_or_equal(date_value, test_date)
        assert result2 is False

    def test_is_date_before_or_equal_with_two_datevalues(self):
        """Test that is_date_before_or_equal works with two DateValue inputs."""
        date_value1 = DateValue(year=2023, month=6, day=15)
        date_value2 = DateValue(year=2023, month=6, day=20)

        result = DateInput.is_date_before_or_equal(date_value1, date_value2)
        assert result is True

    def test_is_date_before_or_equal_with_partial_datevalue_first(self):
        """Test that is_date_before_or_equal handles partial first DateValue."""
        # January 2001 (with default day=1) should be before June 2001 (with default day=1)
        partial_date_value = DateValue(year=2001, month=1)  # Missing day
        later_date = date(2001, 6, 15)

        result = DateInput.is_date_before_or_equal(partial_date_value, later_date)
        assert result is True

    def test_is_date_before_or_equal_with_partial_datevalue_second(self):
        """Test that is_date_before_or_equal handles partial second DateValue."""
        # June 2001 (with default day=1) should be after January 2001 (with default day=1)
        earlier_date = date(2001, 6, 15)
        partial_date_value = DateValue(year=2001, month=1)  # Missing day

        result = DateInput.is_date_before_or_equal(earlier_date, partial_date_value)
        assert result is False

    def test_is_date_before_or_equal_with_both_partial_datevalues(self):
        """Test that is_date_before_or_equal handles both partial DateValues."""
        # January 2001 (with default day=1) should be before December 2001 (with default day=1)
        partial_date_value1 = DateValue(year=2001, month=1)  # Missing day
        partial_date_value2 = DateValue(year=2001, month=12)  # Missing day

        result = DateInput.is_date_before_or_equal(partial_date_value1, partial_date_value2)
        assert result is True

    def test_is_date_before_or_equal_with_partial_dates(self):
        """Test that is_date_before_or_equal works with partial dates using default values."""
        # Test with complete DateValue (should work as before)
        complete_date = DateValue(year=2023, month=6, day=15)
        result = DateInput.is_date_before_or_equal(complete_date, date(2023, 6, 15))
        assert result is True

        # Test with partial DateValue (year only) - should now work with default values
        # 2023-01-01 (default month/day) should be before 2023-06-15
        partial_date = DateValue(year=2023)  # Missing month and day
        result = DateInput.is_date_before_or_equal(partial_date, date(2023, 6, 15))
        assert result is True

        # Test with partial DateValue (month only) - should now work with default values
        # 1900-06-01 (default year/day) should be after 1900-05-30
        partial_date_month = DateValue(month=6)  # Missing year and day
        result = DateInput.is_date_before_or_equal(date(1900, 5, 30), partial_date_month)
        assert result is True

        # Test with partial DateValue (day only) - should now work with default values
        # 1900-01-30 should be after 1900-01-15 (default month=1, day=15)
        partial_date_day = DateValue(day=15)  # Missing year and month (defaults to 1900-01-15)
        result = DateInput.is_date_before_or_equal(date(1900, 1, 30), partial_date_day)
        # 1900-01-30 <= 1900-01-15 should be False
        assert result is False  # 1900-01-30 is NOT before or equal to 1900-01-15

    def test_is_date_before_or_equal_examples_from_issue(self):
        """Test the specific examples mentioned in the issue description."""
        # Example 1: January 2001 is before December 2001
        jan_2001 = DateValue(year=2001, month=1)  # Missing day
        dec_2001 = DateValue(year=2001, month=12)  # Missing day
        result = DateInput.is_date_before_or_equal(jan_2001, dec_2001)
        assert result is True

        # Example 2: 30 March is before 1 May (assuming both use the incomplete default value of 1900)
        mar_30 = DateValue(month=3, day=30)  # Missing year
        may_1 = DateValue(month=5, day=1)  # Missing year
        result = DateInput.is_date_before_or_equal(mar_30, may_1)
        assert result is True  # 1900-03-30 is before 1900-05-01

    def test_is_date_before_or_equal_asymmetric_behavior(self):
        """Test the asymmetric behavior of is_date_before_or_equal."""
        # Test case 1: First date has missing day, second date is complete
        # The second date should be treated as if it also has a missing day
        first_date = DateValue(year=2001, month=1)  # Missing day
        second_date = DateValue(year=2001, month=6, day=15)  # Complete

        # When comparing, second_date should be treated as having a missing day too
        # So we compare 2001-01-01 (default day) with 2001-06-01 (default day)
        # 2001-01-01 <= 2001-06-01 should be True
        result = DateInput.is_date_before_or_equal(first_date, second_date)
        assert result is True

        # Test case 2: First date has missing month, second date is complete
        # The second date should be treated as if it also has a missing month
        first_date = DateValue(year=2001)  # Missing month and day
        second_date = DateValue(year=2001, month=6, day=15)  # Complete

        # When comparing, second_date should be treated as having missing month and day too
        # So we compare 2001-01-01 (default month/day) with 2001-01-01 (default month/day)
        # 2001-01-01 <= 2001-01-01 should be True
        result = DateInput.is_date_before_or_equal(first_date, second_date)
        assert result is True

        # Test case 3: First date is complete, second date has missing components
        # The second date should use default values (no modification)
        first_date = date(2001, 6, 15)  # Complete date object
        second_date = DateValue(year=2001, month=12)  # Missing day

        # When comparing, second_date should use default values
        # So we compare 2001-06-15 with 2001-12-01 (default day)
        # 2001-06-15 <= 2001-12-01 should be True
        result = DateInput.is_date_before_or_equal(first_date, second_date)
        assert result is True

        # Test case 4: Verify the asymmetric behavior - second_date missing components should use defaults
        # When first_date has all components, second_date missing components should use defaults
        first_date = DateValue(year=2001, month=6, day=15)  # Complete
        second_date = DateValue(year=2001, month=12)  # Missing day (should use default day=1)

        # We compare 2001-06-15 with 2001-12-01 (default day)
        # 2001-06-15 <= 2001-12-01 should be True
        result = DateInput.is_date_before_or_equal(first_date, second_date)
        assert result is True

        # Test case 5: Another example of asymmetric behavior
        # First date missing day, second date missing different component
        first_date = DateValue(year=2001, month=6)  # Missing day
        second_date = DateValue(year=2001, day=15)  # Missing month

        # When comparing, second_date should be treated as missing day too (to match first_date)
        # So we compare 2001-06-01 (default day) with 2001-01-01 (default day, since day is now None)
        # 2001-06-01 <= 2001-01-01 should be False
        result = DateInput.is_date_before_or_equal(first_date, second_date)
        assert result is False

    # Property-based tests for is_date_before_or_equal
    @given(
        st.integers(1900, 2100),
        st.integers(1, 12),
        st.integers(1, 28),
        st.integers(1900, 2100),
        st.integers(1, 12),
        st.integers(1, 28),
    )
    def test_is_date_before_or_equal_property_based(self, year1, month1, day1, year2, month2, day2):
        """Property-based test for is_date_before_or_equal with valid dates."""
        date1 = date(year1, month1, day1)
        date2 = date(year2, month2, day2)
        result = DateInput.is_date_before_or_equal(date1, date2)
        expected = date1 <= date2
        assert result == expected

    # Property-based tests for is_date_before_or_equal with DateValue objects
    @given(
        st.integers(1900, 2100),
        st.integers(1, 12),
        st.integers(1, 28),
        st.integers(1900, 2100),
        st.integers(1, 12),
        st.integers(1, 28),
    )
    def test_is_date_before_or_equal_datevalue_property_based(self, year1, month1, day1, year2, month2, day2):
        """Property-based test for is_date_before_or_equal with DateValue objects."""
        date_value1 = DateValue(year=year1, month=month1, day=day1)
        date_value2 = DateValue(year=year2, month=month2, day=day2)
        result = DateInput.is_date_before_or_equal(date_value1, date_value2)
        # Convert to actual dates for comparison
        try:
            date1 = date(year1, month1, day1)
            date2 = date(year2, month2, day2)
            expected = date1 <= date2
            assert result == expected
        except ValueError:
            # Handle invalid dates
            pass

    # Additional tests for get_context_data edge cases
    def test_get_context_data_edge_cases(self):
        """Test that convert_any_date_value_to_date works with partial DateValue objects."""
        # Test with only year
        date_value = DateValue(year=2023)
        result = DateInput.convert_any_date_value_to_date(date_value)
        assert isinstance(result, date)
        assert result.year == 2023
        assert result.month == 1  # Default month
        assert result.day == 1  # Default day

        # Test with only month
        date_value = DateValue(month=6)
        result = DateInput.convert_any_date_value_to_date(date_value)
        assert isinstance(result, date)
        assert result.year == 1900  # Default year
        assert result.month == 6
        assert result.day == 1  # Default day

        # Test with only day
        date_value = DateValue(day=15)
        result = DateInput.convert_any_date_value_to_date(date_value)
        assert isinstance(result, date)
        assert result.year == 1900  # Default year
        assert result.month == 1  # Default month
        assert result.day == 15

        # Test with year and month
        date_value = DateValue(year=2023, month=6)
        result = DateInput.convert_any_date_value_to_date(date_value)
        assert isinstance(result, date)
        assert result.year == 2023
        assert result.month == 6
        assert result.day == 1  # Default day

        # Test with year and day
        date_value = DateValue(year=2023, day=15)
        result = DateInput.convert_any_date_value_to_date(date_value)
        assert isinstance(result, date)
        assert result.year == 2023
        assert result.month == 1  # Default month
        assert result.day == 15

        # Test with month and day
        date_value = DateValue(month=6, day=15)
        result = DateInput.convert_any_date_value_to_date(date_value)
        assert isinstance(result, date)
        assert result.year == 1900  # Default year
        assert result.month == 6
        assert result.day == 15

    # Property-based tests for get_context_data
    @given(st.text(), st.text(), st.text(), st.booleans(), st.booleans(), st.booleans())
    def test_get_context_data_property_based(self, field_id, legend, hint, day, month, year):
        """Property-based test for get_context_data with various parameters."""
        # Skip empty field_id as it would generate a UUID
        if not field_id:
            return

        component = DateInput()
        context = component.get_context_data(
            field_id=field_id,
            legend=legend,
            hint=hint,
            day=day,
            month=month,
            year=year,
        )

        assert context["field_id"] == field_id
        assert context["legend"] == legend
        assert context["hint"] == hint
        assert context["day"] == day
        assert context["month"] == month
        assert context["year"] == year
        assert "date_settings" in context

    # Property-based tests for get_context_data with DateValue values
    @given(st.integers(1, 31), st.integers(1, 12), st.integers(1, 9999))
    def test_get_context_data_with_datevalue_property_based(self, day_val, month_val, year_val):
        """Property-based test for get_context_data with DateValue values."""
        component = DateInput()
        value = DateValue(day=day_val, month=month_val, year=year_val)
        context = component.get_context_data(
            field_id="test-id",
            legend="Test Legend",
            value=value,
            day=True,
            month=True,
            year=True,
        )

        assert context["value_day"] == day_val
        assert context["value_month"] == month_val
        assert context["value_year"] == year_val

    # Tests for get_context_data
    def test_get_context_data_basic(self):
        """Test that get_context_data works with basic parameters."""
        component = DateInput()
        context = component.get_context_data(
            field_id="test-id",
            legend="Test Legend",
            hint="Test Hint",
            day=True,
            month=True,
            year=True,
        )

        assert context["field_id"] == "test-id"
        assert context["legend"] == "Test Legend"
        assert context["hint"] == "Test Hint"
        assert context["day"] is True
        assert context["month"] is True
        assert context["year"] is True
        assert context["value_day"] is None
        assert context["value_month"] is None
        assert context["value_year"] is None
        assert "date_settings" in context

    def test_get_context_data_with_value_dict(self):
        """Test that get_context_data works with a value dictionary."""
        component = DateInput()
        value = DateValue(year=2023, month=6, day=15)
        context = component.get_context_data(
            field_id="test-id",
            legend="Test Legend",
            value=value,
            day=True,
            month=True,
            year=True,
        )

        assert context["value_day"] == 15
        assert context["value_month"] == 6
        assert context["value_year"] == 2023

    def test_get_context_data_with_value_string(self):
        """Test that get_context_data works with a value string."""
        component = DateInput()
        value = '{"year": 2023, "month": 6, "day": 15}'
        context = component.get_context_data(
            field_id="test-id",
            legend="Test Legend",
        )

        # Set the value after initialization to test string parsing
        context = component.get_context_data(
            field_id="test-id",
            legend="Test Legend",
            value=value,
            day=True,
            month=True,
            year=True,
        )

        assert context["value_day"] == 15
        assert context["value_month"] == 6
        assert context["value_year"] == 2023

    def test_get_context_data_with_use_field_value_names(self):
        """Test that get_context_data works with use_field_value_names."""
        component = DateInput()
        value = {"-day": 15, "-month": 6, "-year": 2023}
        context = component.get_context_data(
            field_id="test-id",
            legend="Test Legend",
            value=value,
        )

        # Set the value after initialization to test field value names
        context = component.get_context_data(
            field_id="test-id",
            legend="Test Legend",
            value=value,
            use_field_value_names=True,
            day=True,
            month=True,
            year=True,
        )

        assert context["value_day"] == 15
        assert context["value_month"] == 6
        assert context["value_year"] == 2023

    def test_get_context_data_with_date_settings(self):
        """Test that get_context_data works with date_settings."""
        component = DateInput()
        date_settings = DateSettings(
            day=DateSettingOption(label="Day", field_id="custom-day", display=True),
            month=DateSettingOption(label="Month", field_id="custom-month", display=True),
            year=DateSettingOption(label="Year", field_id="custom-year", display=True),
        )
        context = component.get_context_data(
            field_id="test-id",
            legend="Test Legend",
            date_settings=date_settings,
            day=True,
            month=True,
            year=True,
        )

        assert context["date_settings"]["day"]["label"] == "Day"
        assert context["date_settings"]["day"]["field_id"] == "custom-day"
        assert context["date_settings"]["day"]["display"] is True
        assert context["date_settings"]["month"]["label"] == "Month"
        assert context["date_settings"]["month"]["field_id"] == "custom-month"
        assert context["date_settings"]["month"]["display"] is True
        assert context["date_settings"]["year"]["label"] == "Year"
        assert context["date_settings"]["year"]["field_id"] == "custom-year"
        assert context["date_settings"]["year"]["display"] is True

    def test_get_context_data_with_errors(self):
        """Test that get_context_data works with errors."""
        component = DateInput()
        errors = ["Error 1", "Error 2"]
        context = component.get_context_data(
            field_id="test-id",
            legend="Test Legend",
            errors=errors,
            day=True,
            month=True,
            year=True,
        )

        assert context["errors"] == errors

    def test_get_context_data_with_legend_size(self):
        """Test that get_context_data works with different legend sizes."""
        component = DateInput()
        context = component.get_context_data(
            field_id="test-id",
            legend="Test Legend",
            legend_size="large",
            day=True,
            month=True,
            year=True,
        )

        assert context["legend_size"] == "large"
        assert "govuk-fieldset__legend--l" in context["legend_class"]

        context = component.get_context_data(
            field_id="test-id",
            legend="Test Legend",
            legend_size="medium",
            day=True,
            month=True,
            year=True,
        )

        assert context["legend_size"] == "medium"
        assert "govuk-fieldset__legend--m" in context["legend_class"]

        context = component.get_context_data(
            field_id="test-id",
            legend="Test Legend",
            legend_size="small",
            day=True,
            month=True,
            year=True,
        )

        assert context["legend_size"] == "small"
        assert "govuk-fieldset__legend--s" in context["legend_class"]
