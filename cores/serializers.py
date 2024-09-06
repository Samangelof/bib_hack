from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Book

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'phone_number', 'password', 'fcs')

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            phone_number=validated_data['phone_number'],
            fcs = validated_data["fcs"]
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
            'category',
            'publisher',
            'price_starting_with',
            'publish_date_month',
            'publish_date_year'
        ]