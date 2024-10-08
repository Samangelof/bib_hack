from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Book,
    Discussion,
    Comment,
    UserProfile,
    UserLikedAuthors
)


User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'phone_number', 'password', 'full_name')

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            phone_number=validated_data['phone_number'],
            full_name = validated_data["full_name"]
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            'title',
            'authors',
            'description',
            'categories',
            'published_year',
            'average_rating',
            'num_pages',
            'ratings_count'
        ]

class DiscussionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discussion
        fields = ['id', 'book', 'title', 'created_at', 'updated_at']

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.email')

    class Meta:
        model = Comment
        fields = ['id', 'discussion', 'content', 'created_at', 'updated_at', 'author']


class UserProfileSerializer(serializers.ModelSerializer):
    liked_categories = serializers.StringRelatedField(many=True, source='get_liked_categories')
    liked_authors = serializers.StringRelatedField(many=True, source='get_liked_authors')
    favorite_books = serializers.StringRelatedField(many=True, source='get_favorite_books')
    comments = serializers.StringRelatedField(many=True, source='get_comments')

    class Meta:
        model = UserProfile
        fields = ['user', 'bio', 'profile_image', 'website', 'liked_categories', 'liked_authors', 'favorite_books', 'comments']


class UserLikedAuthorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLikedAuthors
        fields = ['id', 'user', 'author']