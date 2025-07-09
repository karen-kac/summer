from enum import Enum


class Genre(str, Enum):
    experiment = "experiment"
    observation = "observation"
    research = "research"
