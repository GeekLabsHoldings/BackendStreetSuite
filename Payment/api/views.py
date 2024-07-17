from .serializers import UserPaymentSerializer, ProductSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from Payment.models import UserPayment, Product
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.conf import settings
import stripe, json
import stripe.error

stripe.api_key=settings.STRIPE_SECRET_KEY

endpoint_secret = settings.STRIPE_WEBHOOK_KEY

def check_subscription(user_payment, product):
    subscriptions = stripe.Subscription.list(customer=user_payment.stripe_customer_id)
    if user_payment.product != None:
        if subscriptions.data[0].status in ['active'] and user_payment.product.title == product.title:
            return True
    else:
        return False

def create_customer(user):
    customer = stripe.Customer.create(
                            email=user.email,
                            name=f"{user.first_name} {user.last_name}",
                        )
    return customer


class ProductPageView(ListAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
        

class CheckoutPageView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = UserPaymentSerializer
    def get(self, request, id ):
        product = Product.objects.get(id=id) 
        user = request.user
        product_serializer = ProductSerializer(product)
        user_serializer = UserSerializer(user)
        data = {
            'product': product_serializer.data,
            'user': user_serializer.data,
        }
    
        return Response(data)

    def post(self, request, id):
        try:
            product = Product.objects.get(id=id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'})
        
        user = request.user
        serializer = UserPaymentSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            try:                
                user_payment, created = UserPayment.objects.get_or_create(user=user)
                if product.title == 'Weekly Plan' and user_payment.free_trial == True:
                    return Response({'error': 'Weekly Trial is not available for this account.'})
                if check_subscription(user_payment, product):
                    return Response({'error': 'User already has an active subscription.'})
                else:
                    if not user_payment.stripe_customer_id:
                        customer = create_customer(user)
                        user_payment.stripe_customer_id = customer['id']
                    else:
                        customer = stripe.Customer.retrieve(user_payment.stripe_customer_id)
                
                    
                user_payment.product = product
        
                user_payment.save()
                if user_payment.product.title == 'Monthly Plan':
                    user_payment.free_trial = True
                    user_payment.save()
                subscription = stripe.Subscription.create(customer=customer.id, items=[{'price': product.price_id}],
                                        payment_behavior='default_incomplete',
                                        payment_settings={'save_default_payment_method': 'on_subscription'},
                                        expand=['latest_invoice.payment_intent'],)

                return Response({"subscriptionId": subscription.id, "clientSecret" : subscription.latest_invoice.payment_intent.client_secret})
            except stripe.error.StripeError as e:
                return Response({'error': str(e)})
            
        else:
            return Response(serializer.errors)
        
    
@csrf_exempt
@require_POST
def WebHookView(request):
    
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None
    if request.content_type != 'application/json':
        return JsonResponse({'error': 'Content-Type must be application/json'}, status=400)

    payload = request.body
    if not payload:
        return JsonResponse({'error': 'Empty payload'}, status=400)
    try:
        event = json.loads(payload)
    except json.JSONDecodeError as e:
        print(' Webhook error while parsing basic request.' + str(e))
        return JsonResponse({'success': False,
                             'error': 'Webhook error while parsing basic request.' + str(e)})
        
    if endpoint_secret:
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except stripe.SignatureVerificationError as e:
            print(' Webhook signature verification failed.' + str(e))
            return JsonResponse({'success': False,
                                 'error':  'Webhook signature verification failed.' + str(e)})
    
    if event['type'] == 'customer.subscription.created':
        subscription = event['data']['object']
        customer_id = subscription['customer']
        customer = stripe.Customer.retrieve(customer_id)
        customer_email = customer['email']
        if subscription['items']['data']:
            subscription_item = subscription['items']['data'][0]
            plan = subscription_item['plan']
            price_id = plan['id']
        
        product = Product.objects.get(price_id=price_id)
        send_mail(
        'Congratulations',
        f'You have successfully subscribed to {product.title} with {product.amount}$ , this is your customer_id {customer_id} ',
        'your-email@example.com',
        [customer_email], fail_silently=False,
    )
        
    return JsonResponse({'success': True,})


class CancelationPageView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
            try:
                user = request.user
                user_payment = UserPayment.objects.get(user=user)
            except UserPayment.DoesNotExist:
                return Response({'error': 'User payment information not found.'}, status=404)

            
            serializer = UserPaymentSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                try:
                    subscriptions = stripe.Subscription.list(customer=user_payment.stripe_customer_id)
                    delete = False
                    for subscription in subscriptions:
                        if subscription.status == 'active':
                            stripe.Subscription.delete(subscription.id)
                            delete = True
                            break
                    if delete:
                         return Response({'Response': "You have successfully cancelled your subscription! "})
                    else:
                        return Response({'Response': "You have no active subscription to cancel! "})
                except stripe.error.StripeError as e:
                    return Response({'error': str(e)}, status=400)
            else:
                return Response(serializer.errors, status=400)

