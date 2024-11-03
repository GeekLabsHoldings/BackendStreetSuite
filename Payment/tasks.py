from .models import UserPayment, Product
from datetime import datetime
from .api.views import stripe
from celery import shared_task
from django.core.mail import send_mail

@shared_task(queue="Main")
def upgrade_to_monthly():
        users = UserPayment.objects.filter(free_trial=False, product__title="Weekly Plan")
        product = Product.objects.get(title="Monthly Plan")
        for user_payment in users:
            try:
                subscription_list = stripe.Subscription.list(customer=user_payment.stripe_customer_id)
                current_period_end_timestamp = subscription_list.data[0].current_period_end
                if subscription_list.data[0]['items']['data'][0]['price']["recurring"]["interval_count"] == 8:
                    current_period_end = datetime.fromtimestamp(current_period_end_timestamp)
                    payment_method_id = subscription_list.data[0].default_payment_method
                    if current_period_end.date() == datetime.now().date():
                        stripe.Subscription.delete(subscription_list["data"][0]["id"])
                        subscription = stripe.Subscription.create(
                        customer=user_payment.stripe_customer_id,
                        items=[{'price': product.price_id}],
                        payment_behavior='default_incomplete',
                        payment_settings={'save_default_payment_method': 'on_subscription',},
                        default_payment_method=payment_method_id, 
                        expand=['latest_invoice.payment_intent'],
                        )
                        latest_invoice = subscription['latest_invoice']
                        payment_intent = latest_invoice['payment_intent']
                        if payment_intent and payment_intent['status'] == 'requires_confirmation':
                            stripe.PaymentIntent.confirm(payment_intent['id'])
                        print("send mail")
                        send_mail(
                                'StreetSuite',
                                f'You have successfully changed from the Weekly Plan to the {product.title}',
                                'your-email@example.com',
                                [user_payment.user.email], fail_silently=False,
                            )                            
                        user_payment.product = product
                        user_payment.free_trial = True
                        user_payment.save()
            except Exception as e:
                print(f"Error upgrading user {user_payment.user.email}: {e}")
                pass
            

