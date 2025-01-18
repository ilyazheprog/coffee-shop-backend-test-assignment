from modules.dataclasses.payment_statuses import PaymentStatuses

fields = [
    "id",
    "name",
]

data = [
    [
        PaymentStatuses.WAITING_ID,
        PaymentStatuses.WAITING,
    ],
    [
        PaymentStatuses.PAID_ID,
        PaymentStatuses.PAID,
    ],
    [
        PaymentStatuses.CANCELED_ID,
        PaymentStatuses.CANCELED,
    ],
]
