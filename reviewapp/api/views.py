from reviewapp.api.serializers import ReviewSerializer
from reviewapp.models import Review
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated

class ReviewList(ListAPIView):
    serializer_class = ReviewSerializer
    def get_queryset(self):
        order_by = self.request.query_params.get('order_by')
        print(order_by)
        queryset = Review.objects.all()

        if order_by == "most_recent":
            print("aaaaaaaaa")
            return queryset.order_by("-posted_on")[:5]
        else:
            print("bbbbbb")
            return queryset[:5]

class AddReview(CreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes= [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)