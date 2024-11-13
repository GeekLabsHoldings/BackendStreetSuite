from rest_framework import pagination

class BlogPagination(pagination.PageNumberPagination):
    page_size = 15