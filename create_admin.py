#!/usr/bin/env python
import os
import django
import sys

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")
django.setup()

from accounts.models import User

# Create admin user
admin_user = User.objects.create_user(
    username="admin",
    email="admin@wakafine.sl",
    password="admin@1234",
    first_name="Admin",
    last_name="User",
    role="admin",
    is_staff=True,
    is_superuser=True,
)

print("Admin user created successfully!")
print(f"Username: {admin_user.username}")
print(f"Email: {admin_user.email}")
print(f"Role: {admin_user.role}")
