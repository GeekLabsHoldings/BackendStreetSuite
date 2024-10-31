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
    payload = request.body
    event = json.loads(payload)
    
        
    if endpoint_secret:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
            
    if event['type'] == 'invoice.payment_succeeded':    
        invoice = event['data']['object']
        customer_id = invoice.get('customer')
        invoice_id = invoice.get('id')
        customer_email = invoice.get('customer_email')
        customer_name = invoice.get('customer_name')
        invoice_pdf = invoice.get('invoice_pdf')
        plan_id = invoice['lines']['data'][0]['plan']['id']
        product = Product.objects.get(price_id=plan_id)
        send_mail(
            f'StreetSuite_{product.title}',
            f"""Hello {customer_name},
            You have successfully subscribed to {product.title} with {product.amount}$
            Your invoice number is {invoice_id}.
            Your customer id {customer_id}
            Please download the invoice at {invoice_pdf}
            Thank you for your purchase.""",
            'your-email@example.com',
            [customer_email],
        )
        return JsonResponse({'success': True, 'invoice.created': invoice})
    elif event['type'] == 'invoice.upcoming':
        invoice = event['data']['object']
        customer_email = invoice.get('customer_email')
        customer_name = invoice.get('customer_name')
        plan_id = invoice['lines']['data'][0]['plan']['id']
        product = Product.objects.get(price_id=plan_id)
        if product.title == 'Monthly Plan':
            send_mail(
                f'StreetSuite_{product.title}',
                f"""Hello {customer_name},
                Your {product.title} subscription is about to expire.
                Please note that your subscription will automatically renewed.
                Thank you for your understanding.""",
                'your-email@example.com',
                [customer_email],
            )
        elif product.title == 'Weekly Plan':
            send_mail(
                f'StreetSuite_{product.title}',
                f"""Hello {customer_name},
                Your {product.title} subscription is about to expire.
                Please note that your subscription will automatically upgraded to the the Monthly plan .
                Thank you for your understanding.""",
                'your-email@example.com',
                [customer_email],
            )
        product = Product.objects.get(price_id=plan_id)
        return JsonResponse({'success': True, 'invoice.upcoming': invoice})

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