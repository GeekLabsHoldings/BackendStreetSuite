from .models import UserPayment, Product
from datetime import datetime, timedelta
from .api.views import stripe

from django.core.mail import send_mail

def upgrade_to_monthly():
        users = UserPayment.objects.filter(free_trial=False, product__title="Weekly Plan")
        product = Product.objects.get(title="Monthly Plan")
        for user_payment in users:
            subscription_list = stripe.Subscription.list(customer=user_payment.stripe_customer_id)
            current_period_end_timestamp = subscription_list.data[0].current_period_end
            if subscription_list.data[0].items.data[0].plan.interval == 'week':
            # for subscription in subscription_list.data:    
            #     for item in subscription['items']['data']:
            #             if item['plan']['interval'] == 'week':
                current_period_end = datetime.fromtimestamp(current_period_end_timestamp)
                if current_period_end.date() == datetime.now().date():
                    stripe.Subscription.delete(subscription_list.data[0].items.data[0].id)
                    stripe.Subscription.create(customer=user_payment.stripe_customer_id, items=[{'price': product.price_id }])
                    send_mail(
                            'Congratulations',
                            f'You have successfully changed from the Weekly Plan to the {product.title}',
                            'your-email@example.com',
                            [user_payment.user.email], fail_silently=False,
                        )                            
                    user_payment.product = product
                    user_payment.free_trial = True
                    user_payment.save()
                    break

def sending_mails_weekly_plan():
     users = UserPayment.objects.filter(product__title="Weekly Plan")
     for user_payment in users:
        subscription_list = stripe.Subscription.list(customer=user_payment.stripe_customer_id)
        current_period_end_timestamp = subscription_list.data[0].current_period_end
        current_period_end = datetime.fromtimestamp(current_period_end_timestamp)
        if current_period_end.date() == datetime.now().date() + timedelta(days=3):
            send_mail(
                'Your Weekly Plan will expire soon',
                f'Hello, {user_payment.user.first_name}, we would like to inform you that your current plan will expire soon, Regarding our Policies, you will be promoted to the Monthly Plan after the plan expires',
                'your-email@example.com',
                [user_payment.user], fail_silently=False)
            
def sending_mails_monthly_plan():
     users = UserPayment.objects.filter(product__title="Monthly Plan")
     for user_payment in users:
        subscription_list = stripe.Subscription.list(customer=user_payment.stripe_customer_id)
        current_period_end_timestamp = subscription_list.data[0].current_period_end
        current_period_end = datetime.fromtimestamp(current_period_end_timestamp)
        if current_period_end.date() == datetime.now().date() + timedelta(days=3):
            send_mail(
                'Your Plan will expire soon',
                f'Hello, {user_payment.user.first_name}, we would like to inform you that your current plan will expire soon,Regarding our Policies, your plan will be automatically renewed Thanks ',
                'your-email@example.com',
                [user_payment.user], fail_silently=False)