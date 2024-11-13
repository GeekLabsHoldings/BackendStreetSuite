from rest_framework import generics
from BlogApp.models import Post, Category
from BlogApp.api.permissions import IsAuthorOrReadOnly, IsAdminOrReadOnly
from .serializers import PostSerializer, PostListSerializer, CategorySerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from BlogApp.api.pagination import BlogPagination
from BlogApp.consumers import BlogWSConsumer

class BlogPageView(generics.ListAPIView):
    serializer_class = PostListSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    pagination_class = BlogPagination
    filterset_fields = ['categories']
    queryset = Post.objects.all().order_by('-date_posted')

class CategoryView(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = Category.objects.all()

class PostListAdminView(generics.ListAPIView):
    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class PostCreateView(generics.CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAdminOrReadOnly]

    def perform_create(self, serializer):
        post = serializer.save(author=self.request.user)
        BlogWSConsumer.send_new_blog(post)
        
class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthorOrReadOnly]
    lookup_field = 'slug'
    def get_queryset(self, slug):
        return Post.objects.get(slug=slug)