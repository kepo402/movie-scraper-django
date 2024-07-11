from django.shortcuts import render, get_object_or_404
from .models import Content
from django.shortcuts import redirect


def home_redirect(request):
    return redirect('content_list', content_type='movie')

def content_list(request, content_type):
    # Assuming 'type' is a field in your Content model
    contents = Content.objects.filter(type=content_type)
    context = {
        'content_type': content_type,
        'contents': contents,
    }
    return render(request, 'movies/content_list.html', context)

def content_detail(request, content_id):  # Ensure the parameter name matches the URL pattern
    content = get_object_or_404(Content, id=content_id)
    return render(request, 'movies/content_detail.html', {'content': content})


def home(request):
    return redirect('movie_list')

