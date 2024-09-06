from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from cores.views import RegisterView, LoginView, CategoriesView, LikedCategoriesView


urlpatterns = [
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/categories/', CategoriesView.as_view(), name="categories"),
    path("api/liked_categories/", LikedCategoriesView.as_view(), name="liked_categories")
]

{
    "email": "user@example.com",
    "phone_number": "87775554422",
    "password": "your_password"
}