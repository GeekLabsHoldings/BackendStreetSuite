from .models import UserPayment, Product
from datetime import datetime, timedelta
from .api.views import stripe

from django.core.mail import send_mail

def upgrade_to_monthly():
        users = UserPayment.objects.filter(free_trial=False, product__title="Weekly Plan")
        product = Product.objects.get(title="Monthly Plan")
        for user_payment in users:
            print(user_payment)
            subscription_list = stripe.Subscription.list(customer=user_payment.stripe_customer_id)
            # print(subscription_list)
            current_period_end_timestamp = subscription_list.data[0].current_period_end
            if subscription_list.data[0]['items']['data'][0]['price']["recurring"]["interval_count"] == 8:
            # for subscription in subscription_list.data:    
            #     for item in subscription['items']['data']:
            #             if item['plan']['interval'] == 'week':
                current_period_end = datetime.fromtimestamp(current_period_end_timestamp)
                if current_period_end.date() == datetime.now().date():
                    stripe.Subscription.delete(subscription_list.data[0].items.data[0].id)
                    stripe.Subscription.create(customer=user_payment.stripe_customer_id, items=[{'price': product.price_id }])
                    send_mail(
                            'StreetSuite',
                            f'You have successfully changed from the Weekly Plan to the {product.title}',
                            'your-email@example.com',
                            [user_payment.user.email], fail_silently=False,
                        )                            
                    user_payment.product = product
                    user_payment.free_trial = True
                    user_payment.save()

