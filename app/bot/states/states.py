from aiogram.fsm.state import State, StatesGroup


class ClientStates(StatesGroup):
    """Состояния для клиентов."""

    main_menu = State()
    view_menu = State()
    view_orders = State()
    make_order = State()
