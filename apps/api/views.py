# -*- encoding: utf-8 -*-
"""
Copyright (c) 2024 - present TechMinds SL Ltd
"""

from wsgiref.util import request_uri
from django.shortcuts import render   
# Create your views here.   
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.forms.utils import ErrorList
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse
from django import template   
from django.conf import settings 
from django.views import View
import json
from django.http import JsonResponse
from validate_email import validate_email
from django.contrib import messages
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.core.mail import send_mail
from django.template.loader import get_template
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.template.loader import render_to_string
from apps.accounts.utils import account_activation_token
from django.urls import reverse
from django.contrib import auth
from django.contrib.sessions.models import Session
from django.utils import timezone
### accout creations
from django.contrib.auth.models import Group
from validate_email import validate_email
from django.contrib import messages
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.template.loader import render_to_string
from apps.accounts.utils import account_activation_token
from django.urls import reverse
from django.contrib import auth
from django.contrib.auth import authenticate, login, logout
import os
from email.mime.image import MIMEImage

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from datetime import datetime, timedelta
from datetime import datetime, timedelta
from django.conf import settings as setting
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from apps.brutebuster.models import *
from apps.decorators import *
from django.core.cache import cache 
import datetime

from apps.accounts.models import *

from django.http import JsonResponse


from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import permissions, response, views
from rest_framework import viewsets

from django.contrib.auth import authenticate


from apps.home.models import *
# views.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import *
from apps.accounts.views import *
from apps.corecode.models import *
from rest_framework.decorators import action
from rest_framework.views import APIView

from django.http import Http404  # Import Http404

from rest_framework.authtoken.models import Token  # Ensure you have this import if using token authentication
from rest_framework.test import APITestCase, APIClient

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

import jwt   

class LoginView(APIView):

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)

        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

class JitsiTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        room_name = request.query_params.get('room', '*')
        token = self.create_jitsi_jwt(request.user, room_name)
        print(token)
        print(token)
        print(token)
        print(token)
        return Response({"token": token})

    def create_jitsi_jwt(self, user, room_name="*"):
        payload = {
            'aud': 'meet.jit.si',
            'iss': settings.SECRET_KEY,
            'sub': 'meet.jit.si',
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1),
            'room': room_name,
            'context': {
                'user': {
                    'name': user.get_full_name(),
                    'email': user.email,
                    'avatar': getattr(user.profile, 'avatar_url', ''),  # Optional
                    'id': user.id,
                    'moderator': user.is_staff  # Determine if the user is a moderator
                }
            }
        }

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        return token
    
# custom_auth_backend.py

class TokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        if not token:
            return None

        try:
            # Assuming token is in the format 'Token <token>'
            token = token.split(' ')[1]
            user = User.objects.get(auth_token=token)
        except User.DoesNotExist:
            raise AuthenticationFailed('Invalid token')
        
        return (user, None)

# api_views.py


class LoginView(APIView):
    def post(self, request):
        username = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            # Generate token for the authenticated user
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        else:
            return Response({'error': 'Invalid credentials'}, status=400)

class LogoutView(APIView):
    def post(self, request):
        # Delete token upon logout
        request.user.auth_token.delete()
        return Response(status=204)