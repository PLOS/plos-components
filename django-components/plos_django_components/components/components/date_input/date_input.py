"""
A component function which provides the ability to select a date within a form.

This module provides:
- A date input component which provides the ability to select a date within a form
"""

from ast import literal_eval
from datetime import date
from typing import Literal, TypedDict
from uuid import uuid4

from django_components import register
from typing_extensions import NotRequired

from ....utils.govuk_helper import legend_class_from_size
from ..base.base_component import PLOSBaseComponent

DEFAULT_DATE_DAY_VALUE: int = 1
DEFAULT_DATE_MONTH_VALUE: int = 1
DEFAULT_DATE_YEAR_VALUE: int = 1900


class DateSettingOption(TypedDict):
    """
    This class provides the ability to configure settings of a date more easily.
    """

    label: NotRequired[str | None]
    field_id: NotRequired[str | None]
    field_name: NotRequired[str | None]
    display: NotRequired[bool | None]


class DateSettings(TypedDict):
    """
    This class provides the ability to configure each setting individually.
    """

    day: NotRequired[DateSettingOption | None]
    month: NotRequired[DateSettingOption | None]
    year: NotRequired[DateSettingOption | None]


class DateValue(TypedDict):
    """
    TypedDict representing a date with optional day, month, and year components.

    This class represents a date where any of the components can be None,
    representing a partial date.

    Examples:
        DateValue(year=2023, month=6, day=15)  # Complete date
        DateValue(year=2023, month=6)          # Missing day
        DateValue(month=6, day=15)             # Missing year
        DateValue(day=15)                      # Missing year and month
    """

    day: NotRequired[int | None]
    month: NotRequired[int | None]
    year: NotRequired[int | None]


@register("plos_date_input")
class DateInput(PLOSBaseComponent):
    template_name = "date_input.html"

    def get_context_data(
            self,
            field_id: str | None = None,
            legend: str | None = None,
            legend_size: Literal["large", "medium", "small"] = "small",
            hint: str | None = None,
            errors: list[str] | None = None,
            day: bool = True,
            month: bool = True,
            year: bool = True,
            value: DateValue | str | dict | None = None,
            use_field_value_names: bool = False,
            field_value_names: dict | None = None,
            date_settings: DateSettings | None = None,
    ):
        if field_id is None:
            field_id = f"date-input-{uuid4()}"

        if value and isinstance(value, str):
            try:
                value = literal_eval(value)
            except ValueError:
                value = None

        if use_field_value_names and value and isinstance(value, dict):
            # Set default field_value_names if not provided
            if field_value_names is None:
                field_value_names = [
                    {"field_value_name": "-day", "maps_to": "day"},
                    {"field_value_name": "-month", "maps_to": "month"},
                    {"field_value_name": "-year", "maps_to": "year"},
                ]

            temp_value = DateValue()
            flagged: bool = False
            for field_value_name in field_value_names:
                field_name = field_value_name.get("field_value_name")
                val = value.get(field_name)
                if val is not None:
                    flagged = True
                    map_to = field_value_name.get("maps_to")
                    key_finder: Literal["day", "month", "year"] | None = (
                        map_to if map_to in ("day", "month", "year") else None
                    )
                    if key_finder is not None:
                        temp_value[key_finder] = val
            if flagged:
                value = temp_value

        if not value:
            value = {}

        date_settings = self.merge_settings(date_settings, field_id, field_id, day, month, year)

        return {
            "field_id": field_id,
            "legend": legend,
            "legend_class": legend_class_from_size(legend_size),
            "legend_size": legend_size,
            "hint": hint,
            "errors": errors,
            "day": day,
            "month": month,
            "year": year,
            "value_day": value.get("day", None),
            "value_month": value.get("month", None),
            "value_year": value.get("year", None),
            "date_settings": date_settings,
        }

    @staticmethod
    def merge_settings(
            settings: DateSettings | None,
            default_field_id: str,
            default_field_name: str | None,
            day: bool,
            month: bool,
            year: bool,
    ) -> DateSettings:
        """
        Merge the settings which allows mildly flexible settings.
        :param settings: The setting item.
        :param default_field_id: The default field ID.
        :param default_field_name: The default field name.
        :param day: If the day item should be displayed.
        :param month: If the month item should be displayed.
        :param year: If the year item should be displayed.
        :return: The merged setting item.
        """
        if settings is None:
            settings = DateSettings()

        settings["day"] = DateInput.merge_setting_option(
                settings.get("day", None), day, default_field_id, default_field_name, "Day", "day"
        )
        settings["month"] = DateInput.merge_setting_option(
                settings.get("month", None), month, default_field_id, default_field_name, "Month", "month"
        )
        settings["year"] = DateInput.merge_setting_option(
                settings.get("year", None), year, default_field_id, default_field_name, "Year", "year"
        )
        return settings

    @staticmethod
    def merge_setting_option(
            setting: DateSettingOption | None,
            display: bool,
            default_field_id: str,
            default_field_name: str | None,
            default_label: str,
            date_item: Literal["day", "month", "year"],
    ) -> DateSettingOption:
        """
        Merge the settings which allows mildly flexible settings.

        :param setting: The setting item.
        :param display: If the item should be displayed.
        :param default_field_id: The default field ID.
        :param default_field_name: The default field name.
        :param default_label: The default field label.
        :param date_item: The type of date item.
        :return: Return the merged setting item.
        """
        if setting is None:
            setting = DateSettingOption(display=display, label=default_label)

        if setting.get("display", None) is None:
            setting["display"] = display

        if setting.get("field_id", None) is None:
            setting["field_id"] = DateInput.create_default_field_id(default_field_id, date_item)

        if setting.get("field_name", None) is None:
            field_name = default_field_name
            if field_name is None:
                field_name = default_field_id
            setting["field_name"] = DateInput.create_default_field_name(field_name, date_item)

        return setting

    @staticmethod
    def create_default_field_id(field_id: str, date_item: Literal["day", "month", "year"]) -> str:
        """
        Creates the default field ID for a date item.
        :param field_id: The field ID for the parent item.
        :param date_item: Whether this is day, month or year.
        :return: The default field ID.
        """
        return f"{field_id}-{date_item}"

    @staticmethod
    def create_default_field_name(field_name: str, date_item: Literal["day", "month", "year"]) -> str:
        """
        Creates the default field name for a date item.
        :param field_name: The field name for the parent item.
        :param date_item: Whether this is day, month or year.
        :return: The default field name.
        """
        return f"{field_name}-{date_item}"

    @staticmethod
    def convert_to_date(date_value: DateValue | None) -> date | None:
        """
        Convert a DateValue to a Python date object.

        Supports partial dates by using default values for missing components:
        - Default year: 1900
        - Default month: 1 (January)
        - Default day: 1

        Args:
            date_value: The DateValue to convert. Can be a partial date.

        Returns:
            A date object with default values for missing components,
            or None if conversion fails (e.g., invalid date like Feb 30).
        """
        if date_value is None:
            date_value = DateValue()

        # Extract date components with explicit typing
        day_val: int | None = date_value.get("day", None)
        month_val: int | None = date_value.get("month", None)
        year_val: int | None = date_value.get("year", None)

        # Use default values for missing components
        day: int = day_val if day_val is not None else DEFAULT_DATE_DAY_VALUE
        month: int = month_val if month_val is not None else DEFAULT_DATE_MONTH_VALUE
        year: int = year_val if year_val is not None else DEFAULT_DATE_YEAR_VALUE

        try:
            return date(year, month, day)
        except ValueError:
            # Handle invalid dates (e.g., February 30)
            return None

    @staticmethod
    def convert_from_date(date_obj: date) -> DateValue:
        """
        Convert a Python date object to a DateValue.
        :param date_obj: The date object to convert.
        :return: A DateValue dictionary with year, month, and day components.
        """
        return DateValue(year=date_obj.year, month=date_obj.month, day=date_obj.day)

    @staticmethod
    def is_date_before_or_equal(first_date: date | DateValue, second_date: date | DateValue) -> bool:
        """
        Check if the first date is before or equal to the second date.

        Supports comparison of incomplete dates with asymmetric handling:
        - We only compare incomplete objects to incomplete objects
        - The second_date may be more complete than the first object
        - Wherever the first_date has a None DateValue, the second_date should be converted to match
        - The inverse is not true - any None value for the second_date is assumed to be the default value

        For example:
        - January 2001 is before December 2001
        - 30 March is before 1 May (assuming both use the incomplete default value of 1900)

        Args:
            first_date: The first date to compare (date object or DateValue).
            second_date: The second date to compare (date object or DateValue).

        Returns:
            True if first_date is before or equal to second_date, False otherwise.
        """
        # Handle date objects directly
        if isinstance(first_date, date) and isinstance(second_date, date):
            return first_date <= second_date

        # Handle mixed types or DateValue objects
        first_date_obj: date | None = first_date if isinstance(first_date, date) else None
        second_date_obj: date | None = second_date if isinstance(second_date, date) else None

        # Initialize variables to track missing components in first_date
        first_day_missing: bool = False
        first_month_missing: bool = False
        first_year_missing: bool = False

        # Convert first_date to date object if it's a DateValue
        if first_date_obj is None and hasattr(first_date, "keys") and hasattr(first_date, "get"):
            # Check which components are missing in first_date
            first_day_missing = first_date.get("day") is None
            first_month_missing = first_date.get("month") is None
            first_year_missing = first_date.get("year") is None

            # Convert first_date DateValue to date object
            first_date_obj = DateInput.convert_to_date(first_date)

        second_date_value: DateValue = DateValue()
        # Convert second_date to date object if it's a DateValue
        if second_date_obj is None and hasattr(second_date, "keys") and hasattr(second_date, "get"):
            # Match second_date's missing components to first_date's
            second_date_value["day"] = None if first_day_missing else second_date.get("day", None)
            second_date_value["month"] = None if first_month_missing else second_date.get("month", None)
            second_date_value["year"] = None if first_year_missing else second_date.get("year", None)
        elif second_date_obj is not None:
            second_date_value["day"] = None if first_day_missing else second_date_obj.day
            second_date_value["month"] = None if first_month_missing else second_date_obj.month
            second_date_value["year"] = None if first_year_missing else second_date_obj.year

        # Convert the modified second_date
        second_date_obj = DateInput.convert_to_date(second_date_value)

        # Handle None cases
        if first_date_obj is None:
            return False
        if second_date_obj is None:
            return True

        # Perform the comparison
        return first_date_obj <= second_date_obj
