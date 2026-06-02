"""
A component function which provides the ability to select a date within a form.

This module provides:
- A date input component which provides the ability to select a date within a form
"""

from ast import literal_eval
from typing import Literal, TypedDict

from django_components import register
from typing_extensions import NotRequired

from ....utils.govuk_helper import legend_class_from_size
from ..base.base_component import PLOSBaseComponent


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
    Tuples to save content about the date value.
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
        field_value_names: dict | None = [
            dict(field_value_name="-day", maps_to="day"),
            dict(field_value_name="-month", maps_to="month"),
            dict(field_value_name="-year", maps_to="year"),
        ],
        date_settings: DateSettings | None = None,
    ):
        if field_id is None:
            import uuid

            field_id = f"date-input-{uuid.uuid4()}"

        if value and isinstance(value, str):
            try:
                value = literal_eval(value)
            except ValueError:
                value = None

        if use_field_value_names and value and isinstance(value, dict):
            temp_value = DateValue()
            flagged: bool = False
            for field_value_name in field_value_names:
                field_name = field_value_name.get("field_value_name", None)
                val = value.get(field_name, None)
                if val is not None:
                    flagged = True
                    map_to = field_value_name.get("maps_to", None)
                    key_finder: Literal["day", "month", "year"] | None = None
                    if map_to == "day":
                        key_finder = "day"
                    if map_to == "month":
                        key_finder = "month"
                    if map_to == "year":
                        key_finder = "year"
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
