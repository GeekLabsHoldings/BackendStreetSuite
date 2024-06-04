from django.urls import path
from BlogApp.api.views import PostListView, PostDetailView, PostCreateView, PostListAdminView, BlogPageView, CategoryView

urlpatterns = [
    path('', BlogPageView.as_view(), name="blog"),
    path('categories/', CategoryView.as_view(), name="blog"),
    path('archive/', PostListView.as_view(), name="all"),
    path('admin/posts/all/', PostListAdminView.as_view(), name="admin"),
    path('post/new-post/', PostCreateView.as_view(), name='new-post'),
    path('post/<slug:slug>/', PostDetailView.as_view() ,name='post-detail'),
]
