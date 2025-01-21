from dataclasses import dataclass


@dataclass
class DeliveryMethod:
    PICKUP_NAME = "Самовывоз"
    PICKUP_ID = 1
    COURIER_NAME = "Курьер"
    COURIER_ID = 2
    IN_PLACE_NAME = "На месте"
    IN_PLACE_ID = 3
