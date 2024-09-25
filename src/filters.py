from telegram.ext import filters

from settings import ROOT_ID, ADMIN_IDS

class CheckAdmin(filters.User):
    def filter(self, message):
        return message.from_user.id in ADMIN_IDS

check_admin_filter = CheckAdmin(user_id=ADMIN_IDS)