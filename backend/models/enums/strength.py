from enum import Enum


STRENGTH_LABELS = {
    "observation": "観察",
    "writing": "文章を書く",
    "drawing": "絵を描く",
    "crafting": "ものづくり",
    "calculating": "計算・数学",
    "reading": "読書・調査",
    "presentation": "発表・説明",
    "experiment": "実験・検証",
}


class Strength(str, Enum):
    observation = "observation"
    writing = "writing"
    drawing = "drawing"
    calculation = "calculation"
    experiment = "experiment"
    presentation = "presentation"
    research = "research"
    craft = "craft"
    crafting = "crafting"
    calculating = "calculating"
    reading = "reading"

    @property
    def label(self) -> str:
        return STRENGTH_LABELS[self.value]
