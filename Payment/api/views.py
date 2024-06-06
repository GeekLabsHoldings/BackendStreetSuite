from Payment.models import UserPayment, Product
from .serializers import UserPaymentSerializer, ProductSerializer, UserSerializer
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
import stripe
from django.conf import settings


stripe.api_key=settings.STRIPE_SECRET_KEY
class ProductPageView(ListAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
        
         
class CreatePaymentIntent(APIView):
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
        product = Product.objects.get(id=id)
        user = request.user
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            data_dict = serializer.data
            
            data_dict['product'] = {
            'id': product.pk,
            'title': product.title,
            'price_id': product.price_id,
            'amount': product.amount,
            }
            data_dict['user'] = {
                'id': user.pk,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
            print(data_dict)
            response = self.stripe_card_payment(data_dict=data_dict)
        else:
            response = {'errors': serializer.errors}
        return Response(response)
    def stripe_card_payment(self, data_dict): 
        try:
            product = data_dict['product']
            amount = product['amount']
            price = float(amount)*100
            card={
                'number': data_dict['card_number'],
                    'exp_month': data_dict['expiry_month'],
                    'exp_year': data_dict['expiry_year'],
                    'cvc': data_dict['cvv']
                }
            payment_method = stripe.PaymentMethod.create(
                type="card",
                card= card,

            )
            intent= stripe.PaymentIntent.create(
            payment_method=payment_method.id,
            amount = int(price),
            currency='usd',
            confirmation_method='manual',
                    confirm=True,
            )
            
            if intent is not None:
                stripe.PaymentIntent.confirm(intent.id,
                    return_url="http://127.0.0.1:8000/pricing/")
                                 
        except Exception as e:
            return {'error': str(e)}
        #except:
            # response = {
            #     'error': "Your card number is incorrect",
            #     "payment_intent": {"id": "Null"},
            #     "payment_confirm": {'status': "Failed"}
            # }
            #return response
                    
    
    
