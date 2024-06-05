from Payment.models import UserPayment, Product
from .serializers import UserPaymentSerializer, ProductSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
import stripe
from django.conf import settings


stripe.api_key=settings.STRIPE_SECRET_KEY
class ProductPageView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data) 
    
    # def post(self, request):
    #     product_id = request.data.get('product_id')
        

class CreatePaymentIntent(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = UserPaymentSerializer
    lookup_field = 'id'
    def get_object(self):
        queryset = self.get_queryset() 
        pk = self.kwargs.get('id')  
        if pk is not None:
            return queryset.filter(id=pk).first()
        return None
    def get_queryset(self):
        return Product.objects.all()
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response={}
        if serializer.is_valid():
            data_dict = serializer.data
            response = self.stripe_card_payment(data_dict=data_dict)
        else:
            response = {'errors': serializer.errors}
        return Response(response)
    def stripe_card_payment(self, data_dict):
        #try:
            card={
                "number": data_dict['card_number'],
                "exp_month": data_dict['expiry_month'],
                "exp_year": data_dict['expiry_year'],
                "cvc": data_dict['cvc'],
            }
            
            product_id= Product.objects.get(id=product_id)
            print(f"the prduct id is {product_id}")
            if product_id is not None:
                product = Product.objects.get(id=product_id)
                amount = float(product.price)*100
                try:
                    intent= stripe.PaymentIntent.create(
                    amount = int(amount),
                    currency='usd',
                    automatic_payment_methods={
                        'enabled': True
                    })

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
                    
    
    
