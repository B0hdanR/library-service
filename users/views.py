from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiResponse
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from users.serializers import UserRegistrationSerializer, UserSerializer


@extend_schema_view(
    post=extend_schema(
        tags=["Users"],
        summary="Register a new user",
        description="Creates a new user account with an email and password.",
        responses={
            201: UserRegistrationSerializer,
            400: OpenApiResponse(description="Validation error (e.g. email already taken, weak password)."),
        },
    ),
)
class CreateUserView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


@extend_schema_view(
    get=extend_schema(
        tags=["Users"],
        summary="Get my profile",
        description="Returns the profile information of the currently authenticated user.",
        responses={
            200: UserSerializer,
            401: OpenApiResponse(description="Authentication credentials were not provided."),
        },
    ),
    put=extend_schema(
        tags=["Users"],
        summary="Update my profile (full)",
        description="Fully updates the currently authenticated user's profile.",
        responses={
            200: UserSerializer,
            400: OpenApiResponse(description="Validation error."),
            401: OpenApiResponse(description="Authentication credentials were not provided."),
        },
    ),
    patch=extend_schema(
        tags=["Users"],
        summary="Update my profile (partial)",
        description="Partially updates the currently authenticated user's profile.",
        responses={
            200: UserSerializer,
            400: OpenApiResponse(description="Validation error."),
            401: OpenApiResponse(description="Authentication credentials were not provided."),
        },
    ),
)
class UserMeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
