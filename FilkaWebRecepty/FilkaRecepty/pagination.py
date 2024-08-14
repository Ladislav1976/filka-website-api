from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination, CursorPagination

class BlogListCreatePagination(CursorPagination):
    page_size = 2
    ordering = "name"