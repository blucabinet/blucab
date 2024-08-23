from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from main.models import Movie, MovieUserList, UserSettings
from .serializers import MovieSerializer, MovieUserListSerializer


class MovieListApiView(APIView):
    # Add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        movies = Movie.objects.filter()
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MovieApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, ean, *args, **kwargs):
        movies = Movie.objects.filter(ean=ean)
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MovieIdApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id, *args, **kwargs):
        movies = Movie.objects.filter(id=id)
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MovieUserListApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        movies = MovieUserList.objects.filter(user=request.user.id)
        serializer = MovieUserListSerializer(movies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
