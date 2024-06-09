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
    def get(self, request):
        products = Product.objects.all()
        


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
        serializer = UserPaymentSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                token = stripe.Token.create(
                    card={
                        "number": serializer.validated_data['card_number'],
                        "exp_month": serializer.validated_data['expiry_month'],
                        "exp_year": serializer.validated_data['expiry_year'],
                        "cvc": serializer.validated_data['cvv'],
                    }
                )
                
                token_id = token.id

                
                user_payment, created = UserPayment.objects.get_or_create(user=user)
                if not user_payment.stripe_customer_id:
                    customer = stripe.Customer.create(
                        email=user.email,
                        name=f"{user.first_name} {user.last_name}",
                        source=token_id,
                    )
                    user_payment.stripe_customer_id = customer['id']
                else:
                    customer = stripe.Customer.retrieve(user_payment.stripe_customer_id)
                    stripe.Customer.modify(
                        customer.id,
                        source=token_id,
                    )
                user_payment.save()

                
                subscription = stripe.Subscription.create(
                    customer=customer.id,
                    items=[{'price': product.price_id}],
                )

                
                user_payment.product = product
                user_payment.card_number = serializer.validated_data['card_number']
                user_payment.cvv = serializer.validated_data['cvc']
                user_payment.expiry_month = serializer.validated_data['expiry_month']
                user_payment.expiry_year = serializer.validated_data['expiry_year']
                user_payment.save()

                return Response({'subscription': subscription})

            except stripe.error.StripeError as e:
                return Response({'error': str(e)})

        return Response(serializer.errors)
         
# class CreatePaymentIntent(APIView):
#     permission_classes = [IsAuthenticatedOrReadOnly]
#     serializer_class = UserPaymentSerializer
#     def get(self, request, id ):
#         product = Product.objects.get(id=id) 
#         user = request.user
#         product_serializer = ProductSerializer(product)
#         user_serializer = UserSerializer(user)
        
#         data = {
#             'product': product_serializer.data,
#             'user': user_serializer.data,
#         }
    
#         return Response(data)
    
#     def post(self, request, id):
#         product = Product.objects.get(id=id)
#         user = request.user
#         serializer = self.serializer_class(data=request.data)
#         if serializer.is_valid():
#             data_dict = serializer.data
            
#             data_dict['product'] = {
#             'id': product.pk,
#             'title': product.title,
#             'price_id': product.price_id,
#             'amount': product.amount,
#             }
#             data_dict['user'] = {
#                 'id': user.pk,
#                 'email': user.email,
#                 'first_name': user.first_name,
#                 'last_name': user.last_name,
#             }
#             print(data_dict)
#             response = self.stripe_card_payment(data_dict=data_dict)
#         else:
#             response = {'errors': serializer.errors}
#         return Response(response)
#     def stripe_card_payment(self, data_dict): 
#         try:
#             product = data_dict['product']
#             amount = product['amount']
#             price = float(amount)*100
#             card={
#                 'number': data_dict['card_number'],
#                     'exp_month': data_dict['expiry_month'],
#                     'exp_year': data_dict['expiry_year'],
#                     'cvc': data_dict['cvv']
#                 }
#             payment_method = stripe.PaymentMethod.create(
#                 type="card",
#                 card= card,

#             )
#             intent= stripe.PaymentIntent.create(
#             payment_method=payment_method.id,
#             amount = int(price),
#             currency='usd',
#             confirmation_method='manual',
#                     confirm=True,
#             )
            
#             if intent is not None:
#                 stripe.PaymentIntent.confirm(intent.id,
#                     return_url="http://127.0.0.1:8000/pricing/")
                                 
#         except Exception as e:
#             return {'error': str(e)}
#         #except:
#             # response = {
#             #     'error': "Your card number is incorrect",
#             #     "payment_intent": {"id": "Null"},
#             #     "payment_confirm": {'status': "Failed"}
#             # }
#             #return response
                    
    
    
