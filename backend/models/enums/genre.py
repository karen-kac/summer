from enum import Enum

GENRE_LABELS = {
    "experiment": "実験",
    "observation": "観察",
    "research": "調査研究",
}


class Genre(str, Enum):
    experiment = "experiment"
    observation = "observation"
    research = "research"

    @property
    def label(self) -> str:
        return GENRE_LABELS[self.value]
