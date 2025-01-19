from modules.dataclasses import DeliveryMethod

fields = [
    "id",
    "name",
]

data = [
    [DeliveryMethod.PICKUP_ID, DeliveryMethod.PICKUP_NAME],
    [DeliveryMethod.DELIVERY_ID, DeliveryMethod.DELIVERY_NAME],
    [DeliveryMethod.EXPRESS_ID, DeliveryMethod.EXPRESS_NAME],
]
