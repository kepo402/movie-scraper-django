"""
URL configuration for custommoviesite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from movies.views import home
from movies.views import content_list
from movies.views import home_redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', content_list, {'content_type': 'movie'}, name='movie_list'),
    path('movies/', include('movies.urls')),
    path('series/', include('movies.urls')),
]
