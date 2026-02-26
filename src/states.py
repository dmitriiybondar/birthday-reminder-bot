from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    add_birth = State()
    delete_birth = State()
    edit_birth = State()