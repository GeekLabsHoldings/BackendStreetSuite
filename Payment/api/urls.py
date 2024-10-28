from django.urls import path
from .views import ProductPageView, CheckoutPageView, CancelationPageView, testingupgrade, WebHookView

urlpatterns = [
    path('', ProductPageView.as_view(), name="pricing"),
    path('checkout/<int:id>/', CheckoutPageView.as_view(), name='payment_intent'),
    path('webhook/', WebHookView, name='webhook'),
    path('cancel/', CancelationPageView.as_view(), name="cancel"),
    path('test/', testingupgrade.as_view(), name='test')
]   