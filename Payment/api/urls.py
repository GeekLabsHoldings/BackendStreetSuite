from django.urls import path
from .views import ProductPageView, CheckoutPageView, CancelationPageView

urlpatterns = [
    path('', ProductPageView.as_view(), name="pricing"),
    path('cancel/', CancelationPageView.as_view(), name="cancel"),
    path('checkout/<int:id>/', CheckoutPageView.as_view(), name='payment_intent'),

]   