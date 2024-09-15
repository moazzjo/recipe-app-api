"""
 Views for Recipe APIs.
"""


from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets , mixins # type: ignore
from rest_framework.authentication import TokenAuthentication # type: ignore
from rest_framework.permissions import IsAuthenticated # type: ignore

from core.models import Recipe, Tag
from . import serializers

class RecipeViewSet(viewsets.ModelViewSet):
    """ view for manage recipe APIs. """
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-id')
    
    def get_serializer_class(self):
        """ override and return the serializer for the class. """
        if self.action == 'list':
            return serializers.RecipeSerializer
        return self.serializer_class
    
    def perform_create(self, serializer):
        """ create a new recipe """
        serializer.save(user=self.request.user)
    


class TagViewSet(mixins.DestroyModelMixin,
                mixins.UpdateModelMixin,
                mixins.ListModelMixin,
                viewsets.GenericViewSet):
    """ Manage tags in the database. """
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """ Filter queryset to authenticated user. """
        return self.queryset.filter(user = self.request.user).order_by('-name')
         
    
