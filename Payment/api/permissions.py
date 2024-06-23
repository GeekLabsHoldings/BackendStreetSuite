from rest_framework.permissions import BasePermission
from django.conf import settings
import stripe
stripe.api_key=settings.STRIPE_SECRET_KEY

class HasActiveSubscription(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            user_payment = request.user.userpayment
            subscriptions = stripe.Subscription.list(customer=user_payment.stripe_customer_id)
            for subscription in subscriptions:
                if subscription.status == 'active':
                    return True
                else: 
                    return False
        else:
            return False