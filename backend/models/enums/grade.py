from enum import Enum

GRADE_LABELS = {
    "elementary1": "小学1年生",
    "elementary2": "小学2年生",
    "elementary3": "小学3年生",
    "elementary4": "小学4年生",
    "elementary5": "小学5年生",
    "elementary6": "小学6年生",
    "junior1": "中学1年生",
    "junior2": "中学2年生",
    "junior3": "中学3年生",
}


class Grade(str, Enum):
    elementary1 = "elementary1"
    elementary2 = "elementary2"
    elementary3 = "elementary3"
    elementary4 = "elementary4"
    elementary5 = "elementary5"
    elementary6 = "elementary6"
    junior1 = "junior1"
    junior2 = "junior2"
    junior3 = "junior3"

    @property
    def label(self) -> str:
        return GRADE_LABELS[self.value]
