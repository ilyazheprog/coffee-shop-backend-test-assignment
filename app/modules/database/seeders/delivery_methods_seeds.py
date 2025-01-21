from modules.dataclasses import DeliveryMethod

fields = [
    "id",
    "name",
]

data = [
    [DeliveryMethod.PICKUP_ID, DeliveryMethod.PICKUP_NAME],
    [DeliveryMethod.COURIER_ID, DeliveryMethod.COURIER_NAME],
    [DeliveryMethod.IN_PLACE_ID, DeliveryMethod.IN_PLACE_NAME],
]
