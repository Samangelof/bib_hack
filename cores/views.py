from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse, HttpRequest
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from .serializers import RegisterSerializer, DiscussionSerializer, BookSerializer
from .models import (
    Book,
    UserLikedCategories,
    UserProfile,
    CustomUser,
    UserFavoriteBook,
    Discussion
)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user_profile = UserProfile(user=user).save()

            # Генерация JWT токенов
            refresh = RefreshToken.for_user(user)

            return Response({
                "message": "User created successfully",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        # Аутентификация пользователя
        user = authenticate(request, email=email, password=password)

        if user is not None:
            # Генерация JWT токенов
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        else:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class CategoriesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request) -> HttpResponse:
        books = Book.objects.exclude(
            categories__isnull=True).exclude(categories__exact='')
        unique_categories = set()

        for book in books:
            categories_list = book.categories.split(',')

            for category in categories_list:
                unique_categories.add(category.strip())

        return Response({"categories": unique_categories})


class LikedCategoriesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: HttpRequest) -> HttpResponse:
        user_profile = get_object_or_404(UserProfile, user=request.user)
        liked_categories = UserLikedCategories.objects.filter(
            user=user_profile)
        categories_list = [cat.category for cat in liked_categories]

        return Response({"liked_categories": categories_list})

    
    # category : Fiction
    def post(self, request: HttpRequest) -> HttpResponse:
        user = CustomUser.objects.get(email=request.user.email)
        user_profile = UserProfile.objects.get(user=user.id)

        category = request.data.get("category")

        books = Book.objects.exclude(
            categories__isnull=True).exclude(categories__exact='')
        unique_categories = set()

        for book in books:
            categories_list = book.categories.split(',')

            for category_iter in categories_list:
                unique_categories.add(category_iter.strip())

        print(type(category))

        if not category:
            return Response({"error": "Category is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        elif not category in unique_categories:
            return Response({"error": "Category is not found"}, status=status.HTTP_404_NOT_FOUND)
        
        liked_category, created = UserLikedCategories.objects.get_or_create(
            user=user_profile,
            category=category
        )

        if created:
            return Response({"message": "Category added successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Category already exists"}, status=status.HTTP_200_OK)


class RecommendationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs) -> HttpResponse:
        user_profile = get_object_or_404(UserProfile, user=request.user)
        liked_categories = UserLikedCategories.objects.filter(
            user=user_profile).values_list('category', flat=True)

        if not liked_categories:
            return Response({"message": "No liked categories found for recommendations"}, status=status.HTTP_400_BAD_REQUEST)

        # поиск книг, которые принадлежат к любимым категориям пользователя
        recommended_books = Book.objects.filter(
            categories__iregex=r'(?i)\b(?:' + '|'.join(liked_categories) + r')\b')
        books_data = [
            {
                "title": book.title,
                "authors": book.authors,
                "categories": book.categories,
                "thumbnail": book.thumbnail,
                "description": book.description,
                "published_year": book.published_year,
            }
            for book in recommended_books
        ]

        return Response({"recommended_books": books_data}, status=status.HTTP_200_OK)


class FavoriteBookView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        favorite_books = UserFavoriteBook.objects.filter(user=user)
        books_data = [
            {
                "title": fav.book.title,
                "authors": fav.book.authors,
                "isbn13": fav.book.isbn13,
            }
            for fav in favorite_books
        ]
        return Response({"favorites": books_data}, status=status.HTTP_200_OK)

    # book_id : 1
    def post(self, request):
        user = request.user
        book_id = request.data.get("book_id")
        book = get_object_or_404(Book, id=book_id)

        favorite, created = UserFavoriteBook.objects.get_or_create(
            user=user, book=book)

        if created:
            return Response({"message": "Book added to favorites"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Book is already in favorites"}, status=status.HTTP_200_OK)

    def delete(self, request):
        user = request.user
        book_id = request.data.get("book_id")
        book = get_object_or_404(Book, id=book_id)

        favorite = get_object_or_404(UserFavoriteBook, user=user, book=book)
        favorite.delete()

        return Response({"message": "Book removed from favorites"}, status=status.HTTP_204_NO_CONTENT)




# {
#     "book": ["Обязательное поле."],
#     "title": ["Обязательное поле."],
#     "author": ["Обязательное поле."]
# }
class DiscussionListCreateAPIView(APIView):
    """
        получить список обсуждений или создать обсуждение
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        discussions = Discussion.objects.all()
        serializer = DiscussionSerializer(discussions, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DiscussionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DiscussionDetailAPIView(APIView):
    """
        получить, обновить, удалить конкретное обсуждение
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Discussion.objects.get(pk=pk)
        except Discussion.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def get(self, request, pk):
        discussion = self.get_object(pk)
        serializer = DiscussionSerializer(discussion)
        return Response(serializer.data)

    def put(self, request, pk):
        discussion = self.get_object(pk)
        serializer = DiscussionSerializer(discussion, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        discussion = self.get_object(pk)
        discussion.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

# ---------------------------------------------------------------
# список книг и создание новых зкниг
class BookListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Book.objects.all()
    serializer_class = BookSerializer

# ---------------------------------------------------------------
# получение, обновление, удаление
class BookRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Book.objects.all()
    serializer_class = BookSerializer