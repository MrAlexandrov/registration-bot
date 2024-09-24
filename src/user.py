class User:
    def __init__(
        self, 
        user_id, 
        timestamp, 
        username, 
        first_name, 
        last_name, 
        patronymic, 
        study_group, 
        phone_number,
        expectations,
        food_wishes
    ):
        self.user_id = user_id
        self.timestamp = timestamp
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.patronymic = patronymic
        self.study_group = study_group
        self.phone_number = phone_number
        self.expectations = expectations
        self.food_wishes = food_wishes

    def to_dict(self):
        return {
            "user_id":          self.user_id,
            "timestamp":        self.timestamp,
            "username":         self.username,
            "first_name":       self.first_name,
            "last_name":        self.last_name,
            "patronymic":       self.patronymic,
            "study_group":            self.study_group,
            "phone_number":     self.phone_number,
            "expectations":     self.expectations,
            "food_wishes":      self.food_wishes
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            user_id=data.get("user_id"),
            timestamp=data.get("timestamp"),
            username=data.get("username"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            patronymic=data.get("patronymic"),
            study_group=data.get("study_group"),
            phone_number=data.get("phone_number"),
            expectations=data.get("expectations"),
            food_wishes=data.get("food_wishes")
        )

    def __str__(self):
        return (f"User ID: {self.user_id}\n"
                f"Name: {self.first_name} {self.patronymic} {self.last_name}\n"
                f"Username: {self.username}\n"
                f"Group: {self.study_group}\n"
                f"Phone: {self.phone_number}\n"
                f"Expectations: {self.expectations}\n"
                f"Food Wishes: {self.food_wishes}\n"
                f"Registered at: {self.timestamp}\n")

    def __repr__(self):
        return str(self.to_dict())