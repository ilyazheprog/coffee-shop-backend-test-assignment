from dataclasses import dataclass


@dataclass
class OrderStatus:
    PENDING_NAME = "Ожидает обработки"
    PENDING_ID = 1
    PROCESSING_NAME = "Приготовление"
    PROCESSING_ID = 2
    COMPLETED_NAME = "Готов к выдаче"
    COMPLETED_ID = 3
