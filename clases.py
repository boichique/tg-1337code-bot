from aiogram.dispatcher.filters.state import State, StatesGroup

class TaskReport:
    def __init__(self, id, userName, date, level, link, description):
        self.id = id
        self.userName = userName
        self.date = date
        self.level = level
        self.link = link
        self.description = description


class UserState(StatesGroup):
    waiting_for_msg = State()