from django.urls import path
from django.http import HttpResponse


def dummy_view(request):
    return HttpResponse("Hello")


app_name = "accounts"

urlpatterns = [
    path("test/", dummy_view, name="test"),
]
