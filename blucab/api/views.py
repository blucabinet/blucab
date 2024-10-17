# from rest_framework.views import APIView
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from main.models import Movie, MovieUserList, UserSettings
from knox.models import AuthToken
from knox.auth import TokenAuthentication
from .serializers import (
    MovieSerializer,
    MovieUserListSerializer,
    UserSettingsSerializer,
    LoginUserSerializer,
    UserSerializer,
    CreateUserSerializer,
    MovieUserSerializer,
    CreateMovieUserSerializer,
)


class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        return Response(
            {
                "user": UserSerializer(
                    user, context=self.get_serializer_context()
                ).data,
                "token": AuthToken.objects.create(user)[1],
            }
        )


class RegistrationAPIView(generics.GenericAPIView):
    serializer_class = CreateUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "user": UserSerializer(
                    user, context=self.get_serializer_context()
                ).data,
                "token": AuthToken.objects.create(user)[1],
            }, status=status.HTTP_201_CREATED
        )


class MovieListApiView(generics.GenericAPIView):
    # Add permission to check if user is authenticated
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        movies = Movie.objects.filter()
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MovieEanApiView(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, ean, *args, **kwargs):
        movies = Movie.objects.filter(ean=ean)
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MovieIdApiView(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, id, *args, **kwargs):
        movies = Movie.objects.filter(id=id)
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MovieUserListApiView(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = CreateMovieUserSerializer

    def get(self, request, *args, **kwargs):
        movies = MovieUserList.objects.filter(user=request.user.id)
        serializer = MovieUserListSerializer(movies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = serializer.save(user=self.request.user)

        return Response(
            {
                "item": MovieUserSerializer(
                    item, context=self.get_serializer_context()
                ).data,
            }, status=status.HTTP_201_CREATED
        )


class UserSettingsListApiView(generics.GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        settings = UserSettings.objects.filter(user=request.user.id)
        serializer = UserSettingsSerializer(settings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
