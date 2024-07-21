from django.urls import path
from . import views

urlpatterns = [
    path('movies/', views.content_list, {'content_type': 'movie'}, name='movie_list'),
    path('series/', views.content_list, {'content_type': 'series'}, name='series_list'),
    path('nollywood/', views.content_list, {'content_type': 'nollywood'}, name='nollywood_list'),
    path('music/', views.content_list, {'content_type': 'music'}, name='music_list'),
    path('<int:content_id>/', views.content_detail, name='content_detail'),  # Content detail view with reviews
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('search/', views.search, name='search'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('contact-us/', views.contact_us, name='contact_us'),
]

