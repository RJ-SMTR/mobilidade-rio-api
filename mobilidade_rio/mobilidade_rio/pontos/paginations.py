from rest_framework import pagination

class LargePagination(pagination.PageNumberPagination):
    """Add page_size param with big pagination by default"""
    page_size = 500
    page_size_query_param = 'page_size'
    max_page_size = 1000

class CustomPagination(pagination.PageNumberPagination):
    """Add page_size param"""
    page_size_query_param = 'page_size'
    max_page_size = 1000
