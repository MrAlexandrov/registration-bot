from telegram.ext import filters
from settings import ROOT_ID, ADMIN_IDS
from storage import storage

class CheckAdmin(filters.BaseFilter):
    def __init__(self, admin_ids, root_ids):
        self.admin_ids = admin_ids
        self.root_ids = root_ids

    def filter(self, message):
        user_id = str(message.from_user.id)
        return user_id in self.admin_ids or user_id in self.root_ids

check_admin_filter = CheckAdmin(admin_ids=ADMIN_IDS, root_ids=ROOT_ID)

class CheckRoot(filters.BaseFilter):
    def __init__(self, root_ids):
        self.root_ids = root_ids

    def filter(self, message):
        user_id = str(message.from_user.id)
        return user_id in self.root_ids

check_root_filter = CheckRoot(root_ids=ROOT_ID)

class CheckRegistered(filters.BaseFilter):
    def filter(self, message):
        user_id = int(message.from_user.id)
        return True
        # return bool(storage.get_user(user_id=user_id))

check_registered_filter = CheckRegistered()
