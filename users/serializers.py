from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, min_length=3, max_length=150)
    password = serializers.CharField(required=True, min_length=3)

    def validate_username(self, username):
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise ValidationError('User already exists!')


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)