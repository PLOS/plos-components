"""
A component function which provides the ability to select a date within a form.

This module provides:
- A date input component which provides the ability to select a date within a form
"""

from typing import Literal, NamedTuple

from django_components import register

from ..base.base_component import PLOSBaseComponent


class DateValue(NamedTuple):
    """
    Tuples to save content about the date value.
    """

    day: int | None
    month: int | None
    year: int | None


@register("plos_date_input")
class DateInput(PLOSBaseComponent):
    template_name = "date_input.html"

    def get_context_data(
        self,
        legend: str | None = None,
        legend_size: Literal["large", "medium", "small"] = "small",
        hint: str | None = None,
        errors: list[str] | None = None,
        day: bool = True,
        day_name: str | None = "Day",
        month: bool = True,
        month_name: str | None = "Month",
        year: bool = True,
        year_name: str | None = "Year",
        value: DateValue | None = None,
    ):
        return {
            "legend": legend,
            "legend_size": legend_size,
            "hint": hint,
            "errors": errors,
            "day": day,
            "day_name": day_name,
            "month": month,
            "month_name": month_name,
            "year": year,
            "year_name": year_name,
            "value": value,
        }
