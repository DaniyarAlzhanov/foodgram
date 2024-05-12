from rest_framework.pagination import PageNumberPagination


class LimitPaginator(PageNumberPagination):
    """Кастомный пагинатор на ограничение."""

    page_size_query_param = 'limit'
