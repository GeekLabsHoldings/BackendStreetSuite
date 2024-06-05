from Payment.models import UserPayment, Product
from .serializers import UserPaymentSerializer, ProductSerializer
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
        
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    
    def post(self, request, id):
        product = Product.objects.get(id=id)
         
        serializer = self.serializer_class(data=request.data)
        response={}
        if serializer.is_valid():
            data_dict = serializer.data
            print(data_dict)
            product_id = data_dict.get('product_id')
            product = Product.objects.get(id=product_id)
            response = self.stripe_card_payment(data_dict=data_dict, product=product)
        else:
            response = {'errors': serializer.errors}
        return Response(response)
    def stripe_card_payment(self, data_dict, product):
        #try:
            card={
                "number": data_dict['card_number'],
                "exp_month": data_dict['expiry_month'],
                "exp_year": data_dict['expiry_year'],
                "cvv": data_dict['cvv'],
                
            }   
            try:
                price = float(product.amout)*100
                intent= stripe.PaymentIntent.create(
                amount = int(price),
                currency='usd',
                automatic_payment_methods={
                    'enabled': True
                }
                )
                return Response({'client_secret': intent.client_secret})
            except Exception as e:
                return Response({'error': str(e)})
        #except:
            # response = {
            #     'error': "Your card number is incorrect",
            #     "payment_intent": {"id": "Null"},
            #     "payment_confirm": {'status': "Failed"}
            # }
            #return response
                    
    
    
