from django.urls import path
from BlogApp.api.views import PostListView, PostDetailView, PostCreateView, PostListAdminView, BlogPageView

urlpatterns = [
    path('', BlogPageView.as_view(), name="blog"),
    path('posts/all/', PostListView.as_view(), name="all"),
    path('admin/posts/all/', PostListAdminView.as_view(), name="admin"),
    path('post/new-post/', PostCreateView.as_view(), name='new-post'),
    path('post/<slug:slug>/', PostDetailView.as_view() ,name='post-detail'),
]
