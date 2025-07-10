from enum import Enum


DURATION_LABELS = {
    "1week": "1週間",
    "2weeks": "2週間",
    "1month": "1ヶ月",
    "2months": "2ヶ月以上",
    "flexible": "特に決まっていない",
}


class Duration(str, Enum):
    one_week = "1week"
    two_weeks = "2weeks"
    one_month = "1month"
    two_months = "2months"
    flexible = "flexible"

    @property
    def label(self) -> str:
        return DURATION_LABELS[self.value]
