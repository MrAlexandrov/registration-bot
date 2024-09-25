class User:
    def __init__(
        self, 
        user_id, 
        timestamp, 
        username, 
        full_name,
        birth_date,
        study_group, 
        phone_number,
        expectations,
        food_wishes
    ):
        self.user_id = user_id
        self.timestamp = timestamp
        self.username = username
        self.full_name = full_name
        self.birth_date = birth_date
        self.study_group = study_group
        self.phone_number = phone_number
        self.expectations = expectations
        self.food_wishes = food_wishes

    def to_dict(self):
        return {
            "user_id":          self.user_id,
            "timestamp":        self.timestamp,
            "username":         self.username,
            "full_name":        self.full_name,
            "birth_date":       self.birth_date,
            "study_group":      self.study_group,
            "phone_number":     self.phone_number,
            "expectations":     self.expectations,
            "food_wishes":      self.food_wishes
        }

    def to_public_dict(self):
        return {
            "full_name":        self.full_name,
            "birth_date":       self.birth_date,
            "study_group":      self.study_group,
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
            full_name=data.get("full_name"),
            birth_date=data.get("birth_date"),
            study_group=data.get("study_group"),
            phone_number=data.get("phone_number"),
            expectations=data.get("expectations"),
            food_wishes=data.get("food_wishes")
        )

    def __str__(self):
        return (f"ID: {self.user_id}\n"
                f"ФИО: {self.full_name}\n"
                f"День рождения: {self.birth_date}\n"
                f"Nickname: {self.username}\n"
                f"Группа: {self.study_group}\n"
                f"Телефон: {self.phone_number}\n"
                f"Ожидания: {self.expectations}\n"
                f"Особенности питания: {self.food_wishes}\n"
                f"Время: {self.timestamp}\n")

    def __repr__(self):
        return str(self.to_dict())