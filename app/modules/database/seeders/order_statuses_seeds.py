from modules.dataclasses import OrderStatus

fields = [
    "id",
    "name",
]

data = [
    [OrderStatus.PENDING_ID, OrderStatus.PENDING_NAME],
    [OrderStatus.PROCESSING_ID, OrderStatus.PROCESSING_NAME],
    [OrderStatus.COMPLETED_ID, OrderStatus.COMPLETED_NAME],
]
