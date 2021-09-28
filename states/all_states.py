from aiogram.dispatcher.filters.state import State, StatesGroup

class SetupStates(StatesGroup):
    waiting_for_city = State()
    waiting_for_preference = State()
