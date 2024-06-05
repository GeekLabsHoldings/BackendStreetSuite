from django.urls import path
from .views import ProductPageView, CreatePaymentIntent

urlpatterns = [
    path('', ProductPageView.as_view(), name="pricing"),
    path('checkout/<int:pk/', CreatePaymentIntent.as_view(), name='payment_intent'),

]   