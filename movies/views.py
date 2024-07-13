from django.shortcuts import render, get_object_or_404
from .models import Content
from django.shortcuts import redirect
from django.core.paginator import Paginator


def home_redirect(request):
    return redirect('content_list', content_type='movie')

def content_list(request, content_type):
    contents = Content.objects.filter(type=content_type)
    
    paginator = Paginator(contents, 12)  # Show 12 contents per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'content_type': content_type,
        'page_obj': page_obj,  # Replace 'contents' with 'page_obj'
    }
    return render(request, 'movies/content_list.html', context)

def content_detail(request, content_id):  # Ensure the parameter name matches the URL pattern
    content = get_object_or_404(Content, id=content_id)
    return render(request, 'movies/content_detail.html', {'content': content})

def terms_of_service(request):
    return render(request, 'movies/terms_of_service.html')

def search(request):
    query = request.GET.get('query', '')
    movie_results = Content.objects.filter(type='movie', title__icontains=query)
    series_results = Content.objects.filter(type='series', title__icontains=query)
    context = {
        'query': query,
        'movie_results': movie_results,
        'series_results': series_results,
    }
    return render(request, 'movies/search_results.html', context)


def privacy_policy(request):
    return render(request, 'movies/privacy_policy.html')

def contact_us(request):
    return render(request, 'movies/contact_us.html')


def home(request):
    return redirect('movie_list')

