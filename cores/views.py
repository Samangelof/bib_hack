from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse, HttpRequest
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import RegisterSerializer
from .models import Book, UserLikedCategories, UserProfile, CustomUser


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
        books = Book.objects.exclude(categories__isnull=True).exclude(categories__exact='')
        unique_categories = set()

        for book in books:
            categories_list = book.categories.split(',')
        
            for category in categories_list:
                unique_categories.add(category.strip())
        
        return Response({"categories": unique_categories})
    

class LikedCategoriesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: HttpRequest) -> HttpResponse:
        user = CustomUser.objects.get(email=request.user)
        user_profile = UserProfile.objects.get(user=user.id)
        liked_categories = UserLikedCategories.objects.filter(user=user_profile)
    
        categories_list = [cat.category for cat in liked_categories]

        return Response({"liked_categories": categories_list})
    
    def post(self, request: HttpRequest) -> HttpResponse:
        user = CustomUser.objects.get(email=request.user.email)
        user_profile = UserProfile.objects.get(user=user.id)

        category = request.data.get("category")

        if not category:
            return Response({"error": "Category is required"}, status=status.HTTP_400_BAD_REQUEST)

        liked_category, created = UserLikedCategories.objects.get_or_create(
            user=user_profile,
            category=category
        )

        if created:
            return Response({"message": "Category added successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Category already exists"}, status=status.HTTP_200_OK)


class RecomendetionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs) -> HttpResponse:
        pass


# роли:
# юзер
# модератор
# суперпользователь