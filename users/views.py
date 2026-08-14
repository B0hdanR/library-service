from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from users.serializers import UserRegistrationSerializer, UserSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


class UserMeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
