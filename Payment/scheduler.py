from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from django.conf import settings
from .models import UserPayment, Product
from datetime import datetime
from .api.views import stripe
scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")
scheduler.start()

def upgrade_to_monthly():
    try:
        users = UserPayment.objects.filter(free_trial=False, product__title="Weekly Plan")
        product = Product.objects.get(title="Monthly Plan")
        for user_payment in users:

            subscription_list = stripe.Subscription.list(customer=user_payment.stripe_customer_id)
            for subscription in subscription_list.auto_paging_iter():
                current_period_end_timestamp = subscription.current_period_end
            for item in subscription_list['items']['data']:
                    if item['plan']['interval'] == 'week':
                        current_period_end = datetime.fromtimestamp(current_period_end_timestamp)
                        if current_period_end.date() == datetime.now().date():
                            stripe.Subscription.delete(subscription_list.id)
                            stripe.Subscription.create(customer=user_payment.stripe_customer_id, items=[{'price': product.price_id }])
                            user_payment.product = product
                            user_payment.free_trial = True
                            user_payment.save()
                            break
    finally:
         scheduler.shutdown()


# Add the job to the scheduler  
scheduler.add_job(upgrade_to_monthly, trigger='cron', hour=0)