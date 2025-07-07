from enum import Enum


class Duration(str, Enum):
    one_week = "1week"
    two_weeks = "2weeks"
    three_weeks = "3weeks"
    four_weeks = "4weeks"
    longer = "longer"
    one_month = "1month"
    two_months = "2months"
    flexible = "flexible"
