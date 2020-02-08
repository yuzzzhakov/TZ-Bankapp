from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from rest_framework import status
from django.utils import timezone
from rest_framework.viewsets import ModelViewSet
from django.conf import settings
from django.core.mail import send_mail
from .constants import CURR
from .utils import get_bankcard_transactions


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
        try:
            account_id = request.data["account_id"]
        except Exception:
            return Response('no account_id', status=status.HTTP_400_BAD_REQUEST)
        if account_id == "new":
            try:
                user_id = request.data["user_id"]
            except Exception:
                return Response('no user_id', status=status.HTTP_400_BAD_REQUEST)
            try:
                currency = request.data["currency"]
            except Exception:
                return Response('no currency', status=status.HTTP_400_BAD_REQUEST)
            if user_id == "new":
                try:
                    name = request.data["name"]
                    surname = request.data["surname"]
                    phone_number = request.data["phone_number"]
                except Exception:
                    return Response('no name, surname or phone_number', status=status.HTTP_400_BAD_REQUEST)
                user = self.user_create(name, surname, phone_number)
                try:
                    account_id = self.account_create(user, currency)
                except Exception:
                    return Response('invalid currency', status=status.HTTP_400_BAD_REQUEST)
            else:
                try:
                    user = User.objects.get(id=user_id)
                except Exception:
                    return Response('invalid user_id', status=status.HTTP_400_BAD_REQUEST)
                try:
                    account_id = self.account_create(user, currency)
                except Exception:
                    return Response('invalid currency', status=status.HTTP_400_BAD_REQUEST)

        try:
            account = Account.objects.get(id=account_id)
        except Exception:
            return Response('invalid account_id', status=status.HTTP_400_BAD_REQUEST)

        data = {"account": account_id}

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
        return new_user

    def account_create(self, user, currency):
        if currency in CURR:
            new_acc = Account.objects.create(
                owner_info="User account",
                balance=0,
                currency=currency,
                user=user
            )
            return new_acc.id
        else:
            raise Exception


class BankCardBalanceApi(APIView):
    def get_object(self, number):
        bankcard = BankCard.objects.get(number=number)
        return bankcard

    def get(self, request, number, format=None):
        try:
            bankcard = self.get_object(number)
        except Exception:
            return Response('no card with this card_number', status=status.HTTP_404_NOT_FOUND)
        data = {"balance": bankcard.account.balance, "currency": bankcard.account.currency}
        return Response(data)


class BankCardRefill(APIView):
    def post(self, request, format=None):
        try:
            card_number = request.data["card_number"]
        except Exception:
            return Response('no card_number', status=status.HTTP_400_BAD_REQUEST)
        try:
            sum = request.data["sum"]
        except Exception:
            return Response('no sum', status=status.HTTP_400_BAD_REQUEST)
        try:
            currency = request.data["currency"]
        except Exception:
            return Response('no currency', status=status.HTTP_400_BAD_REQUEST)

        try:
            bankcard_account = BankCard.objects.get(number=card_number).account
        except Exception:
            return Response('invalid card_number', status=status.HTTP_400_BAD_REQUEST)

        try:
            if currency != "RUB":
                raise Exception
        except Exception:
            return Response('only RUB available', status=status.HTTP_400_BAD_REQUEST)

        master_account = Account.objects.get(id=2)

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
        try:
            inn = request.data["inn"]
        except Exception:
            return Response('no inn', status=status.HTTP_400_BAD_REQUEST)
        try:
            sum = request.data["sum"]
        except Exception:
            return Response('no sum', status=status.HTTP_400_BAD_REQUEST)
        try:
            currency = request.data["currency"]
        except Exception:
            return Response('no currency', status=status.HTTP_400_BAD_REQUEST)
        try:
            card_number = request.data["card_number"]
        except Exception:
            return Response('no card_number', status=status.HTTP_400_BAD_REQUEST)
        try:
            mail = request.data["mail"]
        except Exception:
            return Response('no mail', status=status.HTTP_400_BAD_REQUEST)
        try:
            bankcard_account = BankCard.objects.get(number=card_number).account
        except Exception:
            return Response('invalid card_number', status=status.HTTP_404_NOT_FOUND)
        try:
            organisation_account = Account.objects.get(owner_info=inn)
        except Exception:
            return Response('invalid inn', status=status.HTTP_400_BAD_REQUEST)

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
        try:
            account = BankCard.objects.get(number=bankcard_number).account
        except Exception:
            return Response('invalid card_number', status=status.HTTP_404_NOT_FOUND)

        data = get_bankcard_transactions(account, n)

        return Response(data)
