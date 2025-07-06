from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),  # /shopping/
    path('recommendations/', views.recommendations, name='recommendations'),  # /shopping/recommendations/
    path('gemini-chat/', views.gemini_chat, name='gemini_chat'),  # /shopping/gemini-chat/
]