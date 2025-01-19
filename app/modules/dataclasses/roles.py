from dataclasses import dataclass


@dataclass
class Role:
    ADMIN_NAME = "ADMIN"
    ADMIN_ID = 1
    BARISTA_NAME = "BARISTA"
    BARISTA_ID = 2
    CLIENT_NAME = "CLIENT"
    CLIENT_ID = 3
