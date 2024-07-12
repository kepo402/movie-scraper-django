from django.urls import path
from . import views

urlpatterns = [
    path('movies/', views.content_list, {'content_type': 'movie'}, name='movie_list'),
    path('series/', views.content_list, {'content_type': 'series'}, name='series_list'),
    path('<int:content_id>/', views.content_detail, name='content_detail'),  # Ensure content_id is captured
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('search/', views.search, name='search'),  # Add this line
    
]
