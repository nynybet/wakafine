#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")
django.setup()

from django.http import JsonResponse
from django.test import RequestFactory, TestCase
from django.contrib.auth.models import AnonymousUser
from accounts.admin_views import UserCreateModalView
from accounts.models import User

# Create a test request factory
factory = RequestFactory()

# Test GET request
request = factory.get("/accounts/admin/users/create/")
request.headers = {"X-Requested-With": "XMLHttpRequest"}

# Create a mock user for authentication
admin_user = User.objects.get(username="admin")
request.user = admin_user

# Test the view
view = UserCreateModalView()
response = view.get(request)

print(f"Response status: {response.status_code}")
print(f"Response content type: {response.get('Content-Type')}")
print(f"Response keys: {list(response.items())}")

if hasattr(response, "content"):
    print(f"Response content preview: {str(response.content)[:200]}")
