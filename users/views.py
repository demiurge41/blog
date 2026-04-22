from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

from .serializers import RegisterSerializer, LoginSerializer


class RegistrationAPIView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data=serializer.errors
            )

        username = serializer.validated_data.get('username')
        password = serializer.validated_data.get('password')

        user = User.objects.create_user(
            username=username,
            password=password
        )

        return Response(
            status=status.HTTP_201_CREATED,
            data={'user_id': user.id}
        )


class AuthorizationAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data=serializer.errors
            )

        username = serializer.validated_data.get('username')
        password = serializer.validated_data.get('password')

        user = authenticate(username=username, password=password)

        if user is None:
            return Response(
                status=status.HTTP_401_UNAUTHORIZED,
                data={'error': 'Invalid username or password'}
            )

        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            status=status.HTTP_200_OK,
            data={'key': token.key}
        )