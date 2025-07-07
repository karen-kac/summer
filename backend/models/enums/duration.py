from enum import Enum


class Duration(str, Enum):
    one_week = "1week"
    two_weeks = "2weeks"
    one_month = "1month"
    two_months = "2months"
    flexible = "flexible"

    _LABELS = {
        "1week": "1週間",
        "2weeks": "2週間",
        "1month": "1ヶ月",
        "2months": "2ヶ月以上",
        "flexible": "特に決まっていない",
    }

    @property
    def label(self) -> str:
        return self._LABELS[self.value]
