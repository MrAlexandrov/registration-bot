class User:
    def __init__(
        self, 
        timestamp, 
        user_id, 
        username, 
        first_name, 
        last_name, 
        patronymic, 
        group, 
        phone_number,
        expectations,
        food_wishes
    ):
        self.timestamp = timestamp
        self.user_id = user_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.patronymic = patronymic
        self.group = group
        self.phone_number = phone_number
        self.expectations = expectations
        self.food_wishes = food_wishes

    def to_dict(self):
        return {
            "timestamp":        self.timestamp,
            "user_id":          self.user_id,
            "username":         self.username,
            "first_name":       self.first_name,
            "last_name":        self.last_name,
            "patronymic":       self.patronymic,
            "group":            self.group,
            "phone_number":     self.phone_number,
            "expectations":     self.expectations,
            "food_wishes":      self.food_wishes
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            timestamp=data.get("timestamp"),
            user_id=data.get("user_id"),
            username=data.get("username"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            patronymic=data.get("patronymic"),
            group=data.get("group"),
            phone_number=data.get("phone_number"),
            expectations=data.get("expectations"),
            food_wishes=data.get("food_wishes")
        )

    def __str__(self):
        return str(self.to_dict())

    def __repr__(self):
        return str(self.to_dict())