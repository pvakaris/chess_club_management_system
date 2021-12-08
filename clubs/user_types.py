from enum import Enum, IntEnum

class UserTypes(IntEnum):
    CLUB_OWNER = 1
    OFFICER = 2
    MEMBER = 3
    APPLICANT = 4

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]
