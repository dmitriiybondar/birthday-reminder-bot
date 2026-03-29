from aiogram.fsm.state import State, StatesGroup

class AddBirthday(StatesGroup):
    add_name = State()
    add_date = State()
    add_tag = State()

class DeleteBirthday(StatesGroup):
    delete_birth = State()

class EditBirthday(StatesGroup):
    edit_name = State()
    select_field = State()
    tag_value = State()
    value = State()

class ListBirthday(StatesGroup):
    choose_tag = State()