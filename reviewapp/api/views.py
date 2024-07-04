from reviewapp.api.serializers import ReviewSerializer
from reviewapp.models import Review
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from BlogApp.api.permissions import IsAdminOrReadOnly

class ReviewList(ListAPIView):
    serializer_class = ReviewSerializer
    def get_queryset(self):
        order_by = self.request.query_params.get('order_by')
        queryset = Review.objects.filter(show=True)

        if order_by == "most_recent":
            return queryset.order_by("-posted_on")[:5]
        else:
            return queryset[:5]

class AddReview(CreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes= [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UpdateReview(UpdateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_url_kwarg = "id"

    def perform_update(self, serializer):
        instance = serializer.instance
        print(instance.show)
        if instance.show == False:
            instance.show = True
        else:
            instance.show = False
        return instance.save()
