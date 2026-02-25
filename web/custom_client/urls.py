from django.urls import path
from . import views

# add patterns here
urlpatterns = [
    path("", views.custom_client, name="custom_client"),
]
