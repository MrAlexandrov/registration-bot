class User:
    def __init__(self, user_id, first_name, last_name, patronymic, group, username):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.patronymic = patronymic
        self.group = group
        self.username = username

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "patronymic": self.patronymic,
            "group": self.group,
            "username": self.username
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            user_id=data.get("user_id"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            patronymic=data.get("patronymic"),
            group=data.get("group"),
            username=data.get("username")
        )

    def __str__(self):
        return str(self.to_dict())

    def __repr__(self):
        return str(self.to_dict())