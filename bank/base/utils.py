from .models import *


def get_bankcard_transactions(account, n):
    inner_transactions_from_list = []
    inner_transactions_to_list = []
    tooutertransaction_list = []
    fromoutertransaction_list = []

    inner_transactions_from = InnerTransaction.objects.filter(trans_from=account).values("transaction_id")
    if inner_transactions_from:
        inner_transactions_from_list.extend(inner_transactions_from)
        for dict in inner_transactions_from_list:
            dict.update({"sign": -1})

    inner_transactions_to = InnerTransaction.objects.filter(trans_to=account).values("transaction_id")
    if inner_transactions_to:
        inner_transactions_to_list.extend(inner_transactions_to)
        for dict in inner_transactions_to_list:
            dict.update({"sign": 1})

    tooutertransaction = ToOuterTransaction.objects.filter(trans_from=account).values("transaction_id")
    if tooutertransaction:
        tooutertransaction_list.extend(tooutertransaction)
        for dict in tooutertransaction_list:
            dict.update({"sign": -1})

    fromoutertransaction = FromOuterTransaction.objects.filter(trans_to=account).values("transaction_id")
    if fromoutertransaction:
        fromoutertransaction_list.extend(fromoutertransaction)
        for dict in fromoutertransaction_list:
            dict.update({"sign": 1})

    transactions = inner_transactions_from_list + inner_transactions_to_list + tooutertransaction_list + fromoutertransaction_list

    for element in transactions:
        element.update({"date_time": Transaction.objects.get(id=element["transaction_id"]).date_time})

    transactions = sorted(transactions, key=lambda x: x["date_time"], reverse=True)
    j = len(transactions)
    data = list()

    for i in range(n):
        if i < j:
            transaction = Transaction.objects.get(id=transactions[i]["transaction_id"])
            data.append({
                "transaction_id": transaction.id,
                "date_time": str(transaction.date_time),
                "sum": transaction.sum * transactions[i]["sign"],
                "currency": transaction.currency
            })
        else:
            break

    return data