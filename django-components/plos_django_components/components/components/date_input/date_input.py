"""
Date input component for Django forms following GOV.UK Design System patterns.

This module provides a comprehensive date input component that renders separate
fields for day, month, and year inputs. It supports various configuration options
for customizing the appearance and behavior of the date input, including:

- Partial date inputs (day, month, or year only)
- Flexible configuration of individual date components
- Date validation and conversion utilities
- Error messaging
- Custom field IDs and names

The module also includes several utility classes and methods for working with dates:
- DateValue: TypedDict for representing date values
- DateSettings: Configuration for date component layouts
- DateSettingOption: Configuration for individual date components
- Conversion utilities for transforming between different date representations
- Date comparison utilities

Usage example:
    {% component "plos_date_input"
        field_id="dob"
        legend="What is your date of birth?"
        hint="For example, 31 3 1980"
        day=True
        month=True
        year=True
        value='{"day": 31, "month": 3, "year": 1980}'
    %}{% endcomponent %}
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


def get_default_date_value() -> date:
    return date(DEFAULT_DATE_YEAR_VALUE, DEFAULT_DATE_MONTH_VALUE, DEFAULT_DATE_DAY_VALUE)


class DateSettingOption(TypedDict):
    """
    Configuration options for individual date components (day, month, or year).

    This TypedDict defines the configuration options available for each individual
    date component within the DateInput component. It allows customization of
    labels, field IDs, field names, and visibility for day, month, and year inputs.

    Attributes:
        label: The label text for the date component. If not provided, a default will be used.
        field_id: The HTML ID attribute for the input field. If not provided, a default will be generated.
        field_name: The HTML name attribute for the input field. If not provided, a default will be generated.
        display: Whether to display this date component. Defaults to True.

    Example:
        # Configure only the day component
        day_setting = DateSettingOption(
            label="Day of birth",
            field_id="dob-day",
            field_name="date_of_birth_day",
            display=True
        )
    """

    label: NotRequired[str | None]
    field_id: NotRequired[str | None]
    field_name: NotRequired[str | None]
    display: NotRequired[bool | None]


class DateSettings(TypedDict):
    """
    Configuration settings for all date components (day, month, and year).

    This TypedDict allows for individual configuration of each date component
    (day, month, and year) through DateSettingOption objects. Each component
    can be configured independently, allowing for flexible date input layouts.

    Attributes:
        day: Configuration for the day input component.
        month: Configuration for the month input component.
        year: Configuration for the year input component.

    Example:
        # Configure all date components with custom settings
        date_settings = DateSettings(
            day=DateSettingOption(label="Day", field_id="custom-day", display=True),
            month=DateSettingOption(label="Month", field_id="custom-month", display=True),
            year=DateSettingOption(label="Year", field_id="custom-year", display=True)
        )

        # Configure only year and month (no day)
        date_settings = DateSettings(
            day=DateSettingOption(display=False),
            month=DateSettingOption(label="Month", field_id="month-input"),
            year=DateSettingOption(label="Year", field_id="year-input")
        )
    """

    day: NotRequired[DateSettingOption | None]
    month: NotRequired[DateSettingOption | None]
    year: NotRequired[DateSettingOption | None]


class DateValue(TypedDict):
    """
    TypedDict representing a date with optional day, month, and year components.

    This class represents a date where any of the components can be None,
    representing a partial date. It's used for both input values to the component
    and for date conversion operations.

    Attributes:
        day: The day component of the date (1-31).
        month: The month component of the date (1-12).
        year: The year component of the date.

    Examples:
        DateValue(year=2023, month=6, day=15)  # Complete date
        DateValue(year=2023, month=6)          # Missing day
        DateValue(month=6, day=15)             # Missing year
        DateValue(day=15)                      # Missing year and month

    Note:
        When components are missing or None, default values are used in date conversions:
        - Default year: 1900
        - Default month: 1 (January)
        - Default day: 1
    """

    day: NotRequired[int | None]
    month: NotRequired[int | None]
    year: NotRequired[int | None]


@register("plos_date_input")
class DateInput(PLOSBaseComponent):
    """
    A Django component that provides a date input field for forms.

    This component renders a date input with separate fields for day, month, and year,
    following the GOV.UK Design System patterns. It supports various configuration
    options for customizing the appearance and behavior of the date input.

    The component handles:
    - Partial date inputs (day, month, or year only)
    - Date validation and conversion
    - Error messaging
    - Custom field IDs and names
    - Flexible configuration of individual date components

    Usage example:
        {% component "plos_date_input"
            field_id="dob"
            legend="What is your date of birth?"
            hint="For example, 31 3 1980"
            day=True
            month=True
            year=True
            value='{"day": 31, "month": 3, "year": 1980}'
        %}{% endcomponent %}

    For more complex configurations, see the date_settings parameter.
    """

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
        """
        Prepare the context data for rendering the date input component.

        Args:
            field_id: Unique identifier for the date input. If not provided, a UUID will be generated.
            legend: The legend text for the date input fieldset.
            legend_size: The size of the legend text. Options are "large", "medium", or "small".
            hint: Optional hint text to display below the legend.
            errors: List of error messages to display for the date input.
            day: Whether to show the day input field.
            month: Whether to show the month input field.
            year: Whether to show the year input field.
            value: The initial value for the date input. Can be a DateValue dict, string
                representation of a dict, or None.
            use_field_value_names: Whether to use custom field value names for mapping values.
            field_value_names: Custom field value names mapping configuration.
            date_settings: Advanced configuration for individual date components (day, month, year).

        Returns:
            dict: Context data for rendering the template.
        """
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
        Merge user-provided date settings with default values.

        This method combines user-provided DateSettings with default values,
        ensuring that all date components (day, month, year) have appropriate
        configuration even when not explicitly specified by the user.

        Args:
            settings: User-provided date settings. Can be None for default behavior.
            default_field_id: The base field ID used to generate default IDs for date components.
            default_field_name: The base field name used to generate default names for date components.
            day: Whether the day component should be displayed.
            month: Whether the month component should be displayed.
            year: Whether the year component should be displayed.

        Returns:
            DateSettings: A complete DateSettings object with all components configured.
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
        Merge individual date component settings with default values.

        This method combines user-provided settings for a single date component
        (day, month, or year) with default values, ensuring that all required
        attributes are present even when not explicitly specified by the user.

        Args:
            setting: User-provided settings for the date component. Can be None for default behavior.
            display: Whether this date component should be displayed.
            default_field_id: The base field ID used to generate the default ID for this component.
            default_field_name: The base field name used to generate the default name for this component.
            default_label: The default label text for this component.
            date_item: The type of date component ("day", "month", or "year").

        Returns:
            DateSettingOption: A complete DateSettingOption object with all attributes configured.
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
        Create a default field ID for a date component.

        This method generates a standardized field ID for individual date components
        by appending the date item type to the parent field ID.

        Args:
            field_id: The base field ID for the date input component.
            date_item: The type of date component ("day", "month", or "year").

        Returns:
            str: The generated field ID for the specific date component.

        Example:
            >>> DateInput.create_default_field_id("date-of-birth", "day")
            "date-of-birth-day"
        """
        return f"{field_id}-{date_item}"

    @staticmethod
    def create_default_field_name(field_name: str, date_item: Literal["day", "month", "year"]) -> str:
        """
        Create a default field name for a date component.

        This method generates a standardized field name for individual date components
        by appending the date item type to the parent field name.

        Args:
            field_name: The base field name for the date input component.
            date_item: The type of date component ("day", "month", or "year").

        Returns:
            str: The generated field name for the specific date component.

        Example:
            >>> DateInput.create_default_field_name("date_of_birth", "month")
            "date_of_birth-month"
        """
        return f"{field_name}-{date_item}"

    @staticmethod
    def convert_to_date(date_value: DateValue | None) -> date:
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
            or a default date if conversion fails (e.g., invalid date like Feb 30).

        Example:
            >>> DateInput.convert_to_date(DateValue(year=2023, month=6, day=15))
            datetime.date(2023, 6, 15)

            >>> DateInput.convert_to_date(DateValue(year=2023, month=6))
            datetime.date(2023, 6, 1)
        """
        if date_value is None:
            date_value = DateValue()

        # Extract date components
        day_val: int | None = date_value.get("day", None)
        month_val: int | None = date_value.get("month", None)
        year_val: int | None = date_value.get("year", None)

        # Use default values for missing components. The value for "day", "month" or "year" may exist but be set to
        # "None". So we have to do this even if it's annoying.
        day: int = day_val if day_val is not None else DEFAULT_DATE_DAY_VALUE
        month: int = month_val if month_val is not None else DEFAULT_DATE_MONTH_VALUE
        year: int = year_val if year_val is not None else DEFAULT_DATE_YEAR_VALUE

        try:
            return date(year, month, day)
        except ValueError:
            # Handle invalid dates (e.g., February 30). This should never happen.
            return get_default_date_value()

    @staticmethod
    def convert_any_date_value_to_date(
        date_value: DateValue | date | None,
        blank_out_day: bool = False,
        blank_out_month: bool = False,
        blank_out_year: bool = False,
    ) -> date:
        """
        Convert any date representation to a date object.

        This method handles multiple input types and can blank out specific components.
        It's particularly useful for date comparisons where only partial date information
        is relevant.

        Args:
            date_value: The date to convert (DateValue, date object, or None).
            blank_out_day: Whether to blank out the day component.
            blank_out_month: Whether to blank out the month component.
            blank_out_year: Whether to blank out the year component.

        Returns:
            A date object with the converted date.

        Example:
            >>> from datetime import date
            >>> DateInput.convert_any_date_value_to_date(date(2023, 6, 15))
            datetime.date(2023, 6, 15)

            >>> DateInput.convert_any_date_value_to_date(
            ...     date(2023, 6, 15),
            ...     blank_out_day=True
            ... )
            datetime.date(2023, 6, 1)
        """
        # Already a date, so we return.
        temp_val: DateValue = DateValue()
        if isinstance(date_value, date):
            if not blank_out_day and not blank_out_month and not blank_out_year:
                return date_value
            else:
                temp_val["day"] = None if blank_out_day else date_value.day
                temp_val["month"] = None if blank_out_month else date_value.month
                temp_val["year"] = None if blank_out_year else date_value.year
        elif isinstance(date_value, dict):
            temp_val["day"] = None if blank_out_day else date_value.get("day", None)
            temp_val["month"] = None if blank_out_month else date_value.get("month", None)
            temp_val["year"] = None if blank_out_year else date_value.get("year", None)
        else:
            temp_val["day"] = DEFAULT_DATE_DAY_VALUE
            temp_val["month"] = DEFAULT_DATE_MONTH_VALUE
            temp_val["year"] = DEFAULT_DATE_YEAR_VALUE

        return DateInput.convert_to_date(temp_val)

    @staticmethod
    def convert_from_date(date_obj: date) -> DateValue:
        """
        Convert a Python date object to a DateValue.

        This method is the inverse of convert_to_date, transforming a standard
        Python date object into a DateValue TypedDict for use with the DateInput
        component or other date-related operations.

        Args:
            date_obj: The date object to convert.

        Returns:
            DateValue: A DateValue dictionary with year, month, and day components.

        Example:
            >>> from datetime import date
            >>> DateInput.convert_from_date(date(2023, 6, 15))
            {'year': 2023, 'month': 6, 'day': 15}
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

        Example:
            >>> from datetime import date
            >>> DateInput.is_date_before_or_equal(
            ...     DateValue(year=2023, month=1),
            ...     DateValue(year=2023, month=12)
            ... )
            True

            >>> DateInput.is_date_before_or_equal(
            ...     date(2023, 6, 15),
            ...     date(2023, 6, 15)
            ... )
            True
        """
        # Handle date objects directly
        if isinstance(first_date, date) and isinstance(second_date, date):
            return first_date <= second_date

        # Handle mixed types or DateValue objects
        first_date_obj: date
        second_date_obj: date

        # Initialize variables to track missing components in first_date
        first_day_missing: bool = False
        first_month_missing: bool = False
        first_year_missing: bool = False

        # Convert first_date to date object if it's a DateValue
        if not isinstance(first_date, date) and hasattr(first_date, "keys") and hasattr(first_date, "get"):
            # Check which components are missing in first_date
            first_day_missing = first_date.get("day", None) is None
            first_month_missing = first_date.get("month", None) is None
            first_year_missing = first_date.get("year", None) is None

        # Convert first_date DateValue to date object
        first_date_obj = DateInput.convert_any_date_value_to_date(first_date)

        # Convert the modified second_date
        second_date_obj = DateInput.convert_any_date_value_to_date(
            second_date, first_day_missing, first_month_missing, first_year_missing
        )

        # Perform the comparison
        return first_date_obj <= second_date_obj
