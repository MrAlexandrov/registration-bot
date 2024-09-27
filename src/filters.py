from telegram.ext import filters

from settings import ROOT_ID, ADMIN_IDS

class CheckAdmin(filters.User):
    def filter(self, message):
        user_id = str(message.from_user.id) 
        return user_id in ADMIN_IDS or user_id in ROOT_ID 
check_admin_filter = CheckAdmin(user_id=ADMIN_IDS)

class CheckRoot(filters.User):
    def filter(self, message):
        user_id = str(message.from_user.id)
        return user_id in ROOT_ID
check_root_filter = CheckRoot(user_id=ROOT_ID)
