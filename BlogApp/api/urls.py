from django.urls import path
from BlogApp.api.views import PostListView, PostDetailView, PostCreateView

urlpatterns = [
    path('admin/all/', PostListView.as_view(), name='admin'),
    path('admin/new-post/', PostCreateView.as_view(), name='new-post'),
    path('<slug:slug>/', PostDetailView.as_view() ,name='post-detail'),
]
