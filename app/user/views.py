"""
Views for the user API
"""

from django.shortcuts import render

from rest_framework import generics, authentication, permissions # type: ignore
from rest_framework.authtoken.views import ObtainAuthToken # type: ignore
from rest_framework.settings import api_settings # type: ignore

from user.serializer import UserSerializer, AuthTokenSerializer

# Create your views here.

class CreateUserView(generics.CreateAPIView):
    """  Create a new user in the system. """
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """ create a new auth token for user. """
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """ Manage the authenticated users"""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """  Retreieve and return the authenticated user. """
        return self.request.user
