from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse, HttpRequest
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .serializers import (
    RegisterSerializer,
    DiscussionSerializer,
    BookSerializer,
    CommentSerializer,
    UserProfileSerializer,
    UserLikedAuthorsSerializer
)
from .models import (
    Book,
    UserLikedCategories,
    UserProfile,
    CustomUser,
    UserFavoriteBook,
    Discussion,
    Comment, 
    UserLikedAuthors
)

import requests
import json


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


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_profile = UserProfile.objects.get(user=request.user)
        serializer = UserProfileSerializer(user_profile)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class LikedAuthorsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: HttpRequest) -> HttpResponse:
        user_profile = get_object_or_404(UserProfile, user=request.user)
        liked_authors = UserLikedAuthors.objects.filter(user=user_profile)
        serializer = UserLikedAuthorsSerializer(liked_authors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: HttpRequest) -> HttpResponse:
        user_profile = get_object_or_404(UserProfile, user=request.user)
        author = request.data.get("author")

        if not author:
            return Response({"error": "Author is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Проверка на существование автора в базе книг
        books = Book.objects.exclude(authors__isnull=True).exclude(authors__exact='')
        unique_authors = {auth.strip() for book in books for auth in book.authors.split(',')}

        if author not in unique_authors:
            return Response({"error": "Author not found"}, status=status.HTTP_404_NOT_FOUND)

        liked_author, created = UserLikedAuthors.objects.get_or_create(
            user=user_profile,
            author=author
        )

        if created:
            return Response({"message": "Author liked successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Author already liked"}, status=status.HTTP_200_OK)
        
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


class LikedAuthorsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: HttpRequest) -> HttpResponse:
        user_profile = get_object_or_404(UserProfile, user=request.user)
        liked_authors = UserLikedAuthors.objects.filter(user=user_profile)
        serializer = UserLikedAuthorsSerializer(liked_authors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: HttpRequest) -> HttpResponse:
        user_profile = get_object_or_404(UserProfile, user=request.user)
        author = request.data.get("author")

        if not author:
            return Response({"error": "Author is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Проверка на существование автора в базе книг
        books = Book.objects.exclude(authors__isnull=True).exclude(authors__exact='')
        unique_authors = set()
        for book in books:
            authors_list = book.authors.split(';')

            for author_iter in authors_list:
                unique_authors.add(author_iter.strip())

        
        if author not in unique_authors:
            return Response({"error": "Author not found"}, status=status.HTTP_404_NOT_FOUND)

        liked_author, created = UserLikedAuthors.objects.get_or_create(
            user=user_profile,
            author=author
        )

        if created:
            return Response({"message": "Author liked successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Author already liked"}, status=status.HTTP_200_OK)

class RecommendationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request) -> HttpResponse:
        user_profile = get_object_or_404(UserProfile, user=request.user)
        user = request.user
        favorite_books = UserFavoriteBook.objects.filter(user=user).all()[:60]
        favorite_books_ids = [favorite_book.book.id for favorite_book in favorite_books]
        favorite_books_list = [
            {"id": book.book.id,
             "title": book.book.title,
             "subtitle": book.book.subtitle,
             "authors": book.book.authors,
             "categories": book.book.categories,
             "thumbnail": book.book.thumbnail,
             "description": book.book.description,
             "published_year": book.book.published_year,
             "average_rating": book.book.average_rating
             } for book in favorite_books]
        liked_categories = UserLikedCategories.objects.filter(
            user=user_profile)
        categories_list = [cat.category for cat in liked_categories]
        books = Book.objects.filter(categories__in=categories_list).exclude(id__in=favorite_books_ids).order_by('?')[:60]
        books_list = [
            {"id": book.id,
             "title": book.title,
             "subtitle": book.subtitle,
             "authors": book.authors,
             "categories": book.categories,
             "thumbnail": book.thumbnail,
             "description": book.description,
             "published_year": book.published_year,
             "average_rating": book.average_rating
             } for book in books]

        messages = [
            {"role": "system", "content": "Вы полезный ассистент, который рекомендует книги на основе любимых книг пользователя и списка доступных книг."},
            {"role": "user", "content": f"Вот список любимых книг пользователя: {favorite_books_list}. На основе этих книг порекомендуйте 10 книг из этого списка: {books_list}. Объясните, почему каждая книга была выбрана, и верните результат в формате JSON с идентификатором книги и причиной для рекомендации. Поля JSON должны быть  id, comment. Ты должен вернуть только JSON без лишнего, только JSON без форматирования. Комментарии должны быть только на русском"}
        ]


        openai_url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-4o",
            "messages": messages,
            "max_tokens": 2000,
            "temperature": 0.7,
            "n": 1,
        }

        response = requests.post(openai_url, headers=headers, json=data)
        print(response.text)

        if response.status_code == 200:
            gpt_response = response.json()['choices'][0]['message']['content']
            gpt_response_json = json.loads(gpt_response)

            return Response({"recommended_books": gpt_response_json}, status=status.HTTP_200_OK)
        else:
            print(response.text)
            return Response({"error": "Failed to get recommendations from GPT"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

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
    


# {"discussion":["Обязательное поле."],"content":["Обязательное поле."]}
class CommentListCreateAPIView(APIView):
    """
    список комментариев к обсуждению или создать ыкомментарий
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, discussion_pk):
        try:
            discussion = Discussion.objects.get(pk=discussion_pk)
        except Discussion.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        comments = discussion.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, discussion_pk):
        try:
            discussion = Discussion.objects.get(pk=discussion_pk)
        except Discussion.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, discussion=discussion)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentDetailAPIView(APIView):
    """
    получить, обновить, удалить конкретный комментарий
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def get(self, request, pk):
        comment = self.get_object(pk)
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    def put(self, request, pk):
        comment = self.get_object(pk)
        if comment.author != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = CommentSerializer(comment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        comment = self.get_object(pk)
        if comment.author != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        comment.delete()
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


class BookSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: HttpRequest) -> HttpResponse:
        query = request.query_params.get('q', None)
        if query:
            books = Book.objects.filter(title__icontains=query)
            serializer = BookSerializer(books, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Query parameter 'q' is required"}, status=status.HTTP_400_BAD_REQUEST)


class AutoComplete(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request: HttpRequest) -> HttpResponse:
        who = request.data.get("who")
        searched = request.data.get("searched")

        if not searched:
            return Response({"error": "Search query is required"}, status=status.HTTP_400_BAD_REQUEST)

        if who == "author":
            results = self.search_author(searched)

        elif who == "book":
            results = self.search_book(searched)

        elif who == "category":
            results = self.search_category(searched)

        else:
            return Response({"error": 'Incorrect "who" value'}, status=status.HTTP_404_NOT_FOUND)

        return Response(results, status=status.HTTP_200_OK)

    def search_author(self, query):
        # Извлекаем всех авторов и разбиваем их по разделителю ';', затем фильтруем
        all_authors = Book.objects.values_list('authors', flat=True)
        unique_authors = set()

        for authors in all_authors:
            # Разделяем строку на отдельных авторов (предполагаем, что они разделены точкой с запятой)
            author_list = authors.split(';')
            for author in author_list:
                if query.lower() in author.strip().lower():  # Фильтруем по введенному запросу
                    unique_authors.add(author.strip())  # Добавляем уникальные имена авторов

        # Возвращаем не более 10 уникальных авторов
        return [{"name": author} for author in list(unique_authors)[:10]]

    def search_book(self, query):
        # Ищем книги по названию или подзаголовку, возвращаем не более 10 результатов
        books = Book.objects.filter(Q(title__icontains=query) | Q(subtitle__icontains=query)).values("id", "title", "subtitle")[:10]
        return list(books)

    def search_category(self, query):
        # Извлекаем уникальные категории, разделяя строки в поле categories
        all_categories = Book.objects.values_list('categories', flat=True)
        unique_categories = set()

        for categories in all_categories:
            # Разделяем строку на отдельные категории (предполагаем, что они разделены запятой)
            category_list = categories.split(',')
            for category in category_list:
                if query.lower() in category.strip().lower():  # Фильтруем по введенному запросу
                    unique_categories.add(category.strip())  # Добавляем категорию в сет (чтобы избежать дубликатов)

        # Возвращаем не более 10 уникальных категорий
        return [{"name": category} for category in list(unique_categories)[:10]]
