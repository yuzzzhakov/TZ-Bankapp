from django.shortcuts import render
from django.views.generic import View
from .models import *


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
        }
        return render(request, 'base/base.html', context=context)

