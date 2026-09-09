from enum import Enum as PyEnum


class Gender(str, PyEnum):
    male = "male"
    female = "female"
    other = "other"
    prefer_not_to_say = "prefer_not_to_say"


class ImageType(str, PyEnum):
    profile_picture = "profile_picture"
    group_picture = "group_picture"
    post_picture = "post_picture"
    group_background_picture = "group_background_picture"


class GroupRole(str, PyEnum):
    member = "member"
    administrator = "administrator"

class FriendRequestStatus(str, PyEnum):
    pending = "pending"
    accepted = "accepted"
    declined = "declined"
    canceled = "canceled"
