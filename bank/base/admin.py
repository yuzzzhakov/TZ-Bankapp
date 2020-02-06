from django.contrib import admin
from .models import *


admin.site.register(User)
admin.site.register(Account)
admin.site.register(BankCard)
admin.site.register(Transaction)
admin.site.register(InnerTransaction)
admin.site.register(ToOuterTransaction)
admin.site.register(FromOuterTransaction)

