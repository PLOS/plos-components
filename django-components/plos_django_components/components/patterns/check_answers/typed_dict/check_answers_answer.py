from typing import TypedDict
from typing_extensions import NotRequired

from ....components.summary_list.summary_list import SummaryListActionTuple


class CheckAnswersAnswer(TypedDict):
    """
    Each answer within a section for checking the answers at the end.
    """

    label: NotRequired[str | None]
    answers: NotRequired[list[str] | None]
    errors: NotRequired[list[str] | None]
    actions: NotRequired[list[SummaryListActionTuple] | None]
