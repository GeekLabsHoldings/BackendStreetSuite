from rest_framework import generics
from BlogApp.models import Post, Category
from BlogApp.api.permissions import IsAuthorOrReadOnly, IsAdminOrReadOnly
from .serializers import PostSerializer, PostListSerializer, CategorySerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta
from BlogApp.consumers import BlogWSConsumer
from rest_framework.permissions import IsAuthenticated
class BlogPageView(generics.ListAPIView):
    serializer_class = PostListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['categories']

    # seven_days_ago = timezone.now() - timedelta(days=7)
    # weekly_queryset = Post.objects.filter(date_posted__gte=seven_days_ago).order_by('-date_posted')
    # if len(weekly_queryset) >= 10:
    #     queryset = weekly_queryset
    # else: 
    #     month_ago = timezone.now() - timedelta(days=30)
    #     queryset = Post.objects.filter(date_posted__gte=month_ago).order_by('-date_posted')
    queryset = Post.objects.all()

class CategoryView(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Category.objects.all()
        
class PostListView(generics.ListAPIView):
    filterset_fields = ['categories']
    queryset = Post.objects.all().order_by('-date_posted')
    serializer_class = PostListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]

class PostListAdminView(generics.ListAPIView):
    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class PostCreateView(generics.CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated , IsAdminOrReadOnly]

    def perform_create(self, serializer):
        post = serializer.save(author=self.request.user)
        BlogWSConsumer.send_new_blog(post)
        
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
        