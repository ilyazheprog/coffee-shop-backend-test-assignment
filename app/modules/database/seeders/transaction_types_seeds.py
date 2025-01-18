from modules.dataclasses import TransactionTypes

fields = [
    "id",
    "name",
]

data = [
    [TransactionTypes.ADD_FUNDS_ID, TransactionTypes.ADD_FUNDS],
    [TransactionTypes.DEBIT_ID, TransactionTypes.DEBIT],
    [TransactionTypes.REFUND_ID, TransactionTypes.REFUND],
    [TransactionTypes.REFERAL_ID, TransactionTypes.REFERAL],
]
