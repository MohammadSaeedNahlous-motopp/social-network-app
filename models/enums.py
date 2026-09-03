from enum import Enum as PyEnum


class Gender(str, PyEnum):
    male = "male"
    female = "female"
    other = "other"
    prefer_not_to_say = "prefer_not_to_say"
