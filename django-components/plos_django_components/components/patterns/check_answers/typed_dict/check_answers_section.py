from typing import Literal, TypedDict

from typing_extensions import NotRequired

from .check_answers_answer import CheckAnswersAnswer


class CheckAnswersSection(TypedDict):
    """
    A section for the check answer pattern.

    label: NotRequired[str | None] The
    """

    label: NotRequired[str | None]
    label_level: NotRequired[Literal[1, 2, 3, 4]]
    field_id: NotRequired[str | None]
    answers: NotRequired[list[CheckAnswersAnswer] | None]
