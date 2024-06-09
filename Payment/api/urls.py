from django.urls import path
from .views import ProductPageView, CheckoutPageView

urlpatterns = [
    path('', ProductPageView.as_view(), name="pricing"),
    path('checkout/<int:id>/', CheckoutPageView.as_view(), name='payment_intent'),

]   