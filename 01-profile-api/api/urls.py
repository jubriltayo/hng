from django.urls import path
from . import views

urlpatterns = [
    path('profiles', views.profile_list, name='profile-list'),
    path('profiles/<str:profile_id>', views.profile_detail, name='profile-detail'),
]