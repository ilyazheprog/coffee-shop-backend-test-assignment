from dataclasses import dataclass


@dataclass
class DeliveryMethod:
    PICKUP_NAME = "PICKUP"
    PICKUP_ID = 1
    DELIVERY_NAME = "DELIVERY"
    DELIVERY_ID = 2
    EXPRESS_NAME = "EXPRESS"
    EXPRESS_ID = 3
