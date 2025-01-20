from sqlalchemy import Column, Integer, ForeignKey, Table

from modules.database.core import Base

# Таблица связи между заказами и позициями меню
order_menu_items = Table(
    "order_menu_items",
    Base.metadata,
    Column("order_id", Integer, ForeignKey("orders.id", ondelete="CASCADE"), primary_key=True),
    Column("menu_item_id", Integer, ForeignKey("menu_items.id", ondelete="CASCADE"), primary_key=True),
    Column("quantity", Integer, nullable=False, default=1),  # Количество позиций в заказе
)