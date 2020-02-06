from django.urls import path
from .views import *
from .apiviews import *
from rest_framework.routers import SimpleRouter


router = SimpleRouter()
router.register('api/users/', UserViewSetApi)
router.register('api/accounts/', AccountViewSetApi)


urlpatterns = [
    path('', InfoListView.as_view()),
]

api_urlpatterns = [
    path('api/bankcards/', BankCardApi.as_view()),
    path('api/bankcards/<str:number>/', BankCardBalanceApi.as_view()),
    path('api/bankcard-refill/', BankCardRefill.as_view()),
    path('api/bankcard-payment/', BankCardPayment.as_view()),
    path('api/bankcard/<str:bankcard_number>/transactions/<int:n>/', BankCardTransactions.as_view()),
]

urlpatterns += router.urls
urlpatterns += api_urlpatterns
