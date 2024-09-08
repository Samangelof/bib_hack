from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from cores.views import (
    RegisterView,
    LoginView,
    CategoriesView,
    LikedCategoriesView,
    RecommendationView,
    FavoriteBookView,
    DiscussionListCreateAPIView,
    DiscussionDetailAPIView,
    BookListCreateView,
    BookRetrieveUpdateDestroyView,
    CommentDetailAPIView,
    CommentListCreateAPIView,
    BookSearchView,
    AutoComplete,
    LikedAuthorsView,
    UserProfileView
)


urlpatterns = [
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/user_profile/', UserProfileView.as_view(), name='user_profile'),

    path('api/login/', LoginView.as_view(), name='login'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('api/categories/', CategoriesView.as_view(), name="categories"),
    path("api/liked_categories/", LikedCategoriesView.as_view(), name="liked_categories"),
    path('api/liked-authors/', LikedAuthorsView.as_view(), name='liked_authors'),
    path('api/recommendations/', RecommendationView.as_view(), name='recommendations'),

    path('api/favorites/', FavoriteBookView.as_view(), name='favorites'),

    path('api/discussions/', DiscussionListCreateAPIView.as_view(), name='discussion_list_create'),
    path('api/discussions/<int:pk>/', DiscussionDetailAPIView.as_view(), name='discussion_detail'),

    path('api/discussions/<int:discussion_pk>/comments/', CommentListCreateAPIView.as_view(), name='comment_list_create'),
    path('api/comments/<int:pk>/', CommentDetailAPIView.as_view(), name='comment_detail'),


    path('api/books/', BookListCreateView.as_view(), name='book_list_create'),
    path('api/books/search/', BookSearchView.as_view(), name='book_search'),
    path('api/books/<int:pk>/', BookRetrieveUpdateDestroyView.as_view(), name='book_detail'),

    path('api/auto_complete/', AutoComplete.as_view(), name="auto_complete")
]


# url: register
# {
#     "email": "user@example.com",
#     "phone_number": "87775554422",
#     "password": "your_password"
# }