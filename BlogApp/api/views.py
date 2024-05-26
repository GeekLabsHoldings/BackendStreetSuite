from rest_framework import generics
from BlogApp.models import Post
from .serializers import PostSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated

class PostListView(generics.ListAPIView):
    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class PostCreateView(generics.CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)   
        
class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self):
        queryset = self.get_queryset()
        slug = self.kwargs.get('slug')  
        if slug is not None:
            return queryset.filter(slug=slug).first()
        return None

    def get_queryset(self):
        return Post.objects.all()
        