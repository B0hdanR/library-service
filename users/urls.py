from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from users.views import CreateUserView, UserMeView


urlpatterns = [
    path("", CreateUserView.as_view(), name="register"),
    path("me/", UserMeView.as_view(), name="me"),
    path("token/", TokenObtainPairView.as_view(), name="token"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

]

app_name = "users"
