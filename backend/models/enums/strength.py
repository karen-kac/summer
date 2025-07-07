from enum import Enum


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

    _LABELS = {
        "observation": "観察",
        "writing": "文章を書く",
        "drawing": "絵を描く",
        "crafting": "ものづくり",
        "calculating": "計算・数学",
        "reading": "読書・調査",
        "presentation": "発表・説明",
        "experiment": "実験・検証",
    }

    @property
    def label(self) -> str:
        return self._LABELS[self.value]
