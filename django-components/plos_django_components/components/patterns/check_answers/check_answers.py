"""
A pattern for displaying answers to check and a button to submit all answers.

This module provides:
- A series of summary list components displaying answers given by the user.
- A submit button.
"""

from typing import Literal

from django_components import register

from ...base.base_component import PLOSBaseComponent
from .typed_dict.check_answers_section import CheckAnswersSection


@register("plos_check_answers")
class CheckAnswers(PLOSBaseComponent):
    """
    A page for displaying answers to check and a button to submit all those answers.

    Example usage::

        {% component "plos_check_answers"
        legend="Examples"
        sections=[
            {
                "label": "Personal details",
                "label_level": 3,
                "answers": [
                    {
                        "label": "Name",
                        "answers": ["Sarah Philips"]
                    },
                    {
                        "label": "Date of birth",
                        "answers": ["5 January 1978"],
                        "actions": [{'name': "Change",'url': "#"}]
                    },
                    {
                        "label": "Customer reference",
                        "answers": ["Not provided"],
                        "actions": [{'name': "Change",'url': "#"}]
                    },
                    {
                        "label": "Address",
                        "answers": ["72 Guild Street", "London", "SE23 6FH"],
                        "actions": [{'name': "Change",'url': "#"}]
                    },
                    {
                        "label": "Contact details",
                        "answers": ["07700 900457", "sarah.phillips@example.com"],
                        "actions": [{'name': "Change",'url': "#"}, {'name': "Add",'url': "#"}]
                    },
                ]
            },
            {
                "label": "Application details",
                "label_level": 3,
                "answers": [
                    {
                        "label": "Previous application number",
                        "answers": ["502135326"],
                        "actions": [{'name': "Change",'url': "#"}]
                    },
                    {
                        "label": "Licence type",
                        "answers": ["For personal use"],
                        "actions": [{'name': "Change",'url': "#"}]
                    },
                    {
                        "label": "Home address",
                        "answers": ["72 Guild Street", "London", "SE23 6FH"],
                        "actions": [{'name': "Change",'url': "#"}]
                    },
                ],
            }
        ] %}
        {% endcomponent %}
    """

    template_name = "check_answers.html"

    def get_context_data(  # noqa: D102
        self,
        /,
        *,
        legend: str | None = None,
        legend_level: Literal[1, 2, 3, 4] = 2,
        field_id: str | None = None,
        submission_disclosure_label: str | None = "Now submit your form",
        submission_disclosure_label_level: Literal[1, 2, 3, 4] = 2,
        submission_disclosure: str | None = (
            "By submitting this form you are confirming that, to the best of your "
            "knowledge, the details you are providing are correct."
        ),
        button_id: str | None = "accept_and_submit",
        button_name: str = "accept_and_submit",
        button_label: str = "Accept and submit",
        sections: list[CheckAnswersSection] | None = None,
    ):

        # Double check the label level.
        if sections is not None:
            for section in sections:
                if section.get("label_level", None) is None:
                    section["label_level"] = 3

        return {
            "legend": legend,
            "legend_level": legend_level,
            "field_id": field_id,
            "submission_disclosure_label": submission_disclosure_label,
            "submission_disclosure_label_level": submission_disclosure_label_level,
            "submission_disclosure": submission_disclosure,
            "button_id": button_id,
            "button_name": button_name,
            "button_label": button_label,
            "sections": sections,
        }
