from django.shortcuts import render
from django.views.generic import View
from .models import *
from .utils import get_bankcard_transactions
from .forms import *


class ControlPanel(View):
    def get(self, request):
        context = {
            'title': 'Control Panel',
            'bankcards': BankCard.objects.all()
        }
        return render(request, 'base/panel.html', context=context)


class CardTransactionsView(View):
    def get(self, request, card_id):
        n = Transaction.objects.all().count()
        data = get_bankcard_transactions(BankCard.objects.get(id=card_id).account, n)
        print(data)
        context = {
            'card_id': card_id,
            'data': data,
            'title': 'Bank Card Transactions',
        }
        return render(request, 'base/card_transactions.html', context=context)


class InfoListView(View):

    def get(self, request):
        users = User.objects.all()
        accounts = Account.objects.all()
        bankcards = BankCard.objects.all()
        transactions = Transaction.objects.all()
        inner_transactions = InnerTransaction.objects.all()
        to_outer_transactions = ToOuterTransaction.objects.all()
        from_outer_transactions = FromOuterTransaction.objects.all()

        context = {
            'users': users,
            'accounts': accounts,
            'bankcards': bankcards,
            'transactions': transactions,
            'inner_transactions': inner_transactions,
            'to_outer_transactions': to_outer_transactions,
            'from_outer_transactions': from_outer_transactions,
            'title': 'System Info',
        }
        return render(request, 'base/info.html', context=context)


class MasterAccountRefill(View):

    def get(self, request):
        context = {
            'form': MasterAccountRefillForm,
            'balance': Account.objects.get(id=2).balance,
            'title': 'Master Account Refill',
        }
        return render(request, 'base/master_account_refill.html', context=context)

    def post(self, request):
        refill = request.POST.get("refill")
        master_account = Account.objects.get(id=2)
        master_account.balance += int(refill)
        master_account.save()
        context = {
            'form': MasterAccountRefillForm,
            'message': f'Master Account Delta = {refill} RUB',
            'balance': Account.objects.get(id=2).balance,
            'title': 'Master Account Refill',
        }
        return render(request, 'base/master_account_refill.html', context=context)


class NewOrgAccount(View):

    def get(self, request):
        context = {
            'form': NewOrgForm,
            'title': 'New Organization Account',
            'message': 'Only RUB account creation available',
        }
        return render(request, 'base/new_org_account.html', context=context)

    def post(self, request):
        owner_info = request.POST.get("INN")
        balance = request.POST.get("balance")
        currency = "RUB"
        account = Account.objects.create(owner_info=owner_info, balance=balance, currency=currency)
        context = {
            'message': 'New Organization Account created:',
            'account': account,
            'title': 'New Organization Account',
        }
        return render(request, 'base/new_org_account.html', context=context)
