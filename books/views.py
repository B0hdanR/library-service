from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets

from books.models import Book
from books.permissions import IsAdminOrReadOnly
from books.serializers import BookSerializer


@extend_schema_view(
    list=extend_schema(
        tags=["Books"],
        description="Retrieve a list of all books available in the library.",
    ),
    retrieve=extend_schema(
        tags=["Books"],
        description="Retrieve detailed information about a specific book.",
    ),
    create=extend_schema(
        tags=["Books"],
        description="Create a new book. Available only to admin users.",
    ),
    update=extend_schema(
        tags=["Books"],
        description="Update a book. Available only to admin users.",
    ),
    partial_update=extend_schema(
        tags=["Books"],
        description="Partially update a book. Available only to admin users.",
    ),
    destroy=extend_schema(
        tags=["Books"],
        description="Delete a book. Available only to admin users.",
    ),
)
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminOrReadOnly]
