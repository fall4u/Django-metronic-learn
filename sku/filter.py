import django_filters

from .models import Book


class BookFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    author = django_filters.CharFilter(lookup_expr='icontains')
    isbn = django_filters.NumberFilter(lookup_expr='icontains')
    press = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Book
        fields = {'name', 'author', 'isbn', 'press'}
