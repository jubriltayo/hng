from django.urls import path
from . import views

urlpatterns = [path("api/classify", views.classify_name, name="classify")]
