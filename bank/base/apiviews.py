from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from rest_framework import status
from django.utils import timezone
from django.http import Http404
from rest_framework.viewsets import ModelViewSet
from django.conf import settings
from django.core.mail import send_mail


class UserViewSetApi(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class AccountViewSetApi(ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


class BankCardApi(APIView):
    def get(self, request, format=None):
        bankcards = BankCard.objects.all()
        serializer = BankCardSerializer(bankcards, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        account_id = request.data["account_id"]
        if account_id == "new":
            user_id = request.data["user_id"]
            currency = request.data["currency"]
            if user_id == "new":
                name = request.data["name"]
                surname = request.data["surname"]
                phone_number = request.data["phone_number"]
                user_id = self.user_create(name, surname, phone_number)
                account_id = self.account_create(user_id, currency)
            else:
                account_id = self.account_create(user_id, currency)

        data = {"account": account_id}
        account = Account.objects.get(id=account_id)

        serializer = BankCardSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            data = serializer.data

            user = account.user
            bankcard = BankCard.objects.get(id=data["id"])
            account_id = data["account"]
            account = Account.objects.get(id=account_id)
            bankcard_balance = account.balance
            currency = account.currency

            del data["id"]
            del data["account"]

            data.update({
                "bankcard_id": bankcard.id,
                "account_id": account_id,
                "user_id": user.id,
                "user_name": user.name,
                "user_surname": user.surname,
                "issue_datetime": timezone.now(),
                "balance": bankcard_balance,
                "currency": currency,
            })

            return Response(data=data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def user_create(self, name, surname, phone_number):
        new_user = User.objects.create(
            name=name,
            surname=surname,
            phone_number=phone_number,
        )
        return new_user.id

    def account_create(self, user_id, currency):
        new_acc = Account.objects.create(
            owner_info="User account",
            balance=0,
            currency=currency,
            user=User.objects.get(id=user_id)
        )
        return new_acc.id


class BankCardBalanceApi(APIView):
    def get_object(self, number):
        try:
            return BankCard.objects.get(number=number)
        except BankCard.DoesNotExist:
            raise Http404

    def get(self, request, number, format=None):
        bankcard = self.get_object(number)
        data = {"balance": bankcard.account.balance, "currency": bankcard.account.currency}
        return Response(data)


class BankCardRefill(APIView):
    def post(self, request, format=None):
        card_number = request.data["card_number"]
        sum = request.data["sum"]
        currency = request.data["currency"]

        master_account = Account.objects.get(id=2)
        bankcard_account = BankCard.objects.get(number=card_number).account

        transaction = Transaction.objects.create(
            sum=sum,
            currency=currency,
            status="IN PROCESS",
        )
        InnerTransaction.objects.create(
            transaction=transaction,
            trans_from=master_account,
            trans_to=bankcard_account,
        )
        data = {
            "transaction_status": transaction.status,
            "transaction_datetime": transaction.date_time,
        }
        return Response(data=data, status=status.HTTP_200_OK)


class BankCardPayment(APIView):
    def post(self, request, format=None):
        inn = request.data["inn"]
        sum = request.data["sum"]
        currency = request.data["currency"]
        card_number = request.data["card_number"]
        mail = request.data["mail"]

        bankcard_account = BankCard.objects.get(number=card_number).account
        organisation_account = Account.objects.get(owner_info=inn)

        transaction = Transaction.objects.create(
            sum=sum,
            currency=currency,
            status="IN PROCESS",
        )
        InnerTransaction.objects.create(
            transaction=transaction,
            trans_from=bankcard_account,
            trans_to=organisation_account,
        )

        data = {
            "transaction_status": transaction.status,
            "transaction_datetime": transaction.date_time,
        }

        send_mail('Transaction', str(data), settings.EMAIL_HOST_USER, [mail])

        return Response(data=data, status=status.HTTP_200_OK)


class BankCardTransactions(APIView):
    def get(self, request, bankcard_number, n, format=None):
        account = BankCard.objects.get(number=bankcard_number).account
        transactions = []
        inner_transactions_from = InnerTransaction.objects.filter(trans_from=account).values("transaction_id")
        if inner_transactions_from:
            transactions.extend(inner_transactions_from)
        inner_transactions_to = InnerTransaction.objects.filter(trans_to=account).values("transaction_id")
        if inner_transactions_to:
            transactions.extend(inner_transactions_to)
        tooutertransaction = ToOuterTransaction.objects.filter(trans_from=account).values("transaction_id")
        if tooutertransaction:
            transactions.extend(tooutertransaction)
        fromoutertransaction = FromOuterTransaction.objects.filter(trans_to=account).values("transaction_id")
        if fromoutertransaction:
            transactions.extend(fromoutertransaction)

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
                    "sum": transaction.sum,
                    "currency": transaction.currency
                })
            else:
                break

        return Response(data)
