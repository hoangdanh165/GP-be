from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    page_size = 5
    page_query_param = "page"
    max_page_size = 10


class CustomPaginationSR(PageNumberPagination):
    page_size = 7
    page_query_param = "page"
    max_page_size = 10


class CustomPaginationNotification(PageNumberPagination):
    page_size = 7
    page_query_param = "page"
    max_page_size = 10


class CustomPaginationPayment(PageNumberPagination):
    page_size = 10
    page_query_param = "page"
    max_page_size = 10
