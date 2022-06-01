from aiogram.dispatcher.filters.state import State, StatesGroup

class Start(StatesGroup):
    waiting_for_city = State()
    specifying_city = State()
