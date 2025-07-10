from enum import Enum


INTEREST_LABELS = {
    "science": "理科・科学",
    "nature": "自然・環境",
    "animals": "動物・生物",
    "cooking": "料理・食べ物",
    "art": "美術・工作",
    "sports": "スポーツ・運動",
    "music": "音楽・楽器",
    "history": "歴史・社会",
    "technology": "プログラミング・技術",
    "math": "数学・計算",
}


class Interest(str, Enum):
    science = "science"
    nature = "nature"
    technology = "technology"
    art = "art"
    sports = "sports"
    music = "music"
    cooking = "cooking"
    animals = "animals"
    history = "history"
    math = "math"

    @property
    def label(self) -> str:
        return INTEREST_LABELS[self.value]
