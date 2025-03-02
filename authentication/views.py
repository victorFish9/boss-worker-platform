from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate
from rest_framework.serializers import ModelSerializer


# 🔹 Сериализатор для пользователя
class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email")


# 🔹 Регистрация нового пользователя
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email")

        if User.objects.filter(username=username).exists():
            return Response({"error": "Пользователь уже существует"}, status=400)

        user = User.objects.create_user(username=username, password=password, email=email)
        return Response({"message": "Пользователь зарегистрирован"}, status=201)


# 🔹 Вход и получение токена
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)
        if user is None:
            return Response({"error": "Неверные учетные данные"}, status=401)

        refresh = RefreshToken.for_user(user)
        return Response({"access": str(refresh.access_token), "refresh": str(refresh)})


# 🔹 Получение данных текущего пользователя
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
