from aiogram.fsm.state import State, StatesGroup

class OrderStates(StatesGroup):
    waiting_for_nickname = State()
    waiting_for_username = State()
    waiting_for_address = State()
    waiting_for_product_type = State()
    waiting_for_quantity = State()
    waiting_for_price = State()
    waiting_for_cash_amount = State()
    waiting_for_credit_amount = State()
    waiting_for_notes = State()
    showing_summary = State()
    # States חדשים לעריכה
    selecting_product_to_edit = State()
    choosing_edit_action = State()
    editing_product_type = State()
    editing_quantity = State()
    editing_price = State()