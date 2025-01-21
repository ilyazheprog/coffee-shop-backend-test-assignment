from dataclasses import dataclass


@dataclass
class Buttons:
    """Кнопки для бота."""

    MENU = "Меню"
    ORDERS = "Заказы"
    STATUS = "Статус"
    SET_STATUS = "Установить статус"
    STATUSES = "Статусы"
    BACK = "Назад"
    PICKUP = "Самовывоз"
    DELIVERY = "Доставка"
    EXPRESS = "Экспресс"
    CANCEL = "Отмена"
    CONFIRM = "Подтвердить"
    CONFIRM_ORDER = "Подтвердить заказ"
    CANCEL_ORDER = "Отменить заказ"
    MAKE_ORDER = "Оформить заказ"
    NEXT = "Далее"
    PREVIOUS = "Назад"
    SET_DELIVERY_METHOD = "Выбрать способ доставки"
    SET_ORDER = "Установить заказ"
    SET_ORDER_STATUS = "Установить статус заказа"
    SET_ORDER_DELIVERY_METHOD = "Установить способ доставки"
