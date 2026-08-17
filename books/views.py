from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
)
from rest_framework import viewsets

from books.models import Book
from books.permissions import IsAdminOrReadOnly
from books.serializers import BookSerializer


@extend_schema_view(
    list=extend_schema(
        tags=["Books"],
        summary="List books",
        description=(
                "Retrieve a list of all books available in the library. "
                "Available to anyone, including unauthenticated users."
        ),
        responses={200: BookSerializer(many=True)},
        examples=[
            OpenApiExample(
                "Example response",
                value=[
                    {
                        "id": 1,
                        "title": "The Hobbit",
                        "author": "J.R.R. Tolkien",
                        "cover": "HARD",
                        "inventory": 5,
                        "daily_fee": "1.50",
                    }
                ],
                response_only=True,
            ),
        ],
    ),
    retrieve=extend_schema(
        tags=["Books"],
        summary="Retrieve a book",
        description="Retrieve detailed information about a specific book.",
        responses={
            200: BookSerializer,
            404: OpenApiResponse(description="Book not found."),
        },
    ),
    create=extend_schema(
        tags=["Books"],
        summary="Add a new book",
        description="Create a new book. Available only to admin users.",
        responses={
            201: BookSerializer,
            401: OpenApiResponse(description="Authentication credentials were not provided."),
            403: OpenApiResponse(description="Only admin users can perform this action."),
        },
        examples=[
            OpenApiExample(
                "Example response",
                value=[
                    {
                        "id": 1,
                        "title": "The Hobbit",
                        "author": "J.R.R. Tolkien",
                        "cover": "HARD",
                        "inventory": 5,
                        "daily_fee": "1.50",
                    }
                ],
                response_only=True,
            ),
        ],
    ),
    update=extend_schema(
        tags=["Books"],
        summary="Update a book",
        description="Fully update a book, including managing its inventory. Available only to admin users.",
        responses={
            200: BookSerializer,
            401: OpenApiResponse(description="Authentication credentials were not provided."),
            403: OpenApiResponse(description="Only admin users can perform this action."),
        },
    ),
    partial_update=extend_schema(
        tags=["Books"],
        summary="Partially update a book",
        description="Partially update a book, including managing its inventory. Available only to admin users.",
        responses={
            200: BookSerializer,
            401: OpenApiResponse(description="Authentication credentials were not provided."),
            403: OpenApiResponse(description="Only admin users can perform this action."),
        },
    ),
    destroy=extend_schema(
        tags=["Books"],
        summary="Delete a book",
        description="Delete a book. Available only to admin users.",
        responses={
            204: OpenApiResponse(description="Book deleted successfully."),
            401: OpenApiResponse(description="Authentication credentials were not provided."),
            403: OpenApiResponse(description="Only admin users can perform this action."),
        },
    ),
)
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminOrReadOnly]
