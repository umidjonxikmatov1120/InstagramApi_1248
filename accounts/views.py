from django.shortcuts import render
from .models import User
from .serializers import SignUpSerializer
from rest_framework import generics


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer