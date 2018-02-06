import django_filters

from .models import Book, LibBook


class BookFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    author = django_filters.CharFilter(lookup_expr='icontains')
    isbn = django_filters.NumberFilter(lookup_expr='icontains')
    press = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Book
        fields = {'name', 'author', 'isbn', 'press'}


class LibBookFilter(django_filters.FilterSet):
    book__name = django_filters.CharFilter(lookup_expr='icontains')
    book__isbn = django_filters.NumberFilter(lookup_expr='icontains')
    status     = django_filters.ChoiceFilter(choices=LibBook.STATUS_CHOICES)

    class Meta:
        model = LibBook
        fields = {'book__name', 'uuid', 'status', 'book__isbn'}
