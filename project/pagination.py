from rest_framework.pagination import PageNumberPagination


class ProjectPagination(PageNumberPagination):
    page_query_param='p'
    page_size=10
