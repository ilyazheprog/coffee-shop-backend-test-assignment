from dataclasses import dataclass


@dataclass
class OrderStatus:
    PENDING_NAME = "PENDING"
    PENDING_ID = 1
    PROCESSING_NAME = "PROCESSING"
    PROCESSING_ID = 2
    COMPLETED_NAME = "COMPLETED"
    COMPLETED_ID = 3
