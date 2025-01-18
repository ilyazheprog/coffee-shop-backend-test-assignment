fields = [
    "id",
    "user_id",
    "key_value",
    "device_type_id",
    "server_id",
    "is_active",
    "inactive_date",
    "date_first_payment",
    "date_next_payment",
    "price",
]

data = [
    [
        1,  # id
        7658129475,  # user_id
        "example_key_1",  # key_value
        1,  # device_type_id (e.g., pc)
        1,  # server_id
        True,  # is_active
        None,  # inactive_date (None if active)
        "2024-01-01 12:00:00",  # date_first_payment
        "2024-10-17 18:05:00",  # date_next_payment
        9.99,  # price
    ],
    [
        2,  # id
        7658129475,  # user_id
        "example_key_2",  # key_value
        2,  # device_type_id (e.g., mob)
        1,  # server_id
        False,  # is_active
        "2024-03-01 12:00:00",  # inactive_date (e.g., past date)
        "2024-01-01 12:00:00",  # date_first_payment
        None,  # date_next_payment (None if not active)
        15.99,  # price
    ],
]
