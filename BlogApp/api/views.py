from rest_framework import generics
from BlogApp.models import Post
from BlogApp.api.permissions import IsAuthorOrReadOnly, IsAdminOrReadOnly
from .serializers import PostSerializer, PostListSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend


class BlogPageView(generics.ListAPIView):
    queryset = Post.objects.all().order_by('-date_posted')[:20]
    serializer_class = PostListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['tags']
class PostListView(generics.ListAPIView):
    queryset = Post.objects.all().order_by('-date_posted')[:20]
    serializer_class = PostListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['tags']

class PostListAdminView(generics.ListAPIView):
    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class PostCreateView(generics.CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated , IsAdminOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)   
        
class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly , IsAuthorOrReadOnly ]
    lookup_field = 'slug'
    def get_object(self):
        queryset = self.get_queryset()
        slug = self.kwargs.get('slug')  
        if slug is not None:
            return queryset.filter(slug=slug).first()
        return None

    def get_queryset(self):
        return Post.objects.all()
        