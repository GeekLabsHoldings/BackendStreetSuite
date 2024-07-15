from .serializers import UserPaymentSerializer, ProductSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from Payment.models import UserPayment, Product
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from django.core.mail import send_mail
import stripe
from django.conf import settings
stripe.api_key=settings.STRIPE_SECRET_KEY

def check_subscription(user_payment):
    subscriptions = stripe.Subscription.list(customer=user_payment.stripe_customer_id)
    if user_payment.product != None:
        for subscription in subscriptions:
            if subscription.status in ['active', 'trialing'] and user_payment.product.title == 'Monthly Plan':
                return True
            else: 
                return False
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
                    return Response({'error': 'User has already used the Weekly trial.'})
                if check_subscription(user_payment):
                    return Response({'error': 'User already has an active subscription.'})
                else:
                    if not user_payment.stripe_customer_id:
                        customer = create_customer(user)
                        user_payment.stripe_customer_id = customer['id']
                    else:
                        customer = stripe.Customer.retrieve(user_payment.stripe_customer_id)
                user_payment.product = product
                user_payment.save()
                subscription = stripe.Subscription.create(customer=customer.id, items=[{'price': product.price_id}],
                                        payment_behavior='default_incomplete',
                                        payment_settings={'save_default_payment_method': 'on_subscription'},
                                        expand=['latest_invoice.payment_intent'],)
                send_mail(
                        'Congratulations',
                        f'You have successfully subscribed to {product.title} with {product.amount}$',
                        'your-email@example.com',
                        [user.email], fail_silently=False,
                    )
                return Response({"subscriptionId": subscription.id, "clientSecret" : subscription.latest_invoice.payment_intent.client_secret})
            except stripe.error.StripeError as e:
                return Response({'error': str(e)})
            
        else:
            return Response(serializer.errors)
        
class Test(APIView):
    def get(self, request):
        
        payment_method = stripe.Customer.list_payment_methods("cus_QTOxAmLkUPNP2l", limit=3)
        
        return Response({"payment_methods": payment_method['data'],
                         "payment_method_id": payment_method['data'][0].id})
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

