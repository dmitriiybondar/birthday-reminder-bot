from aiogram.fsm.state import State, StatesGroup

class Tag(StatesGroup):
    add_tag = State()
    delete_tag = State()

class EditTag(StatesGroup):
    choose_tag = State()
    value = State()