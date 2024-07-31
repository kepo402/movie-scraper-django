from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from .models import Content, Review
from .forms import ReviewForm
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_http_methods

def home_redirect(request):
    return redirect('content_list', content_type='movie')

from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Content  # Adjust the import based on your app's structure

def content_list(request, content_type):
    contents = Content.objects.filter(type=content_type).order_by('-date_added')
    paginator = Paginator(contents, 12)  # Show 12 contents per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Calculate page numbers to show
    current_page = page_obj.number
    total_pages = page_obj.paginator.num_pages
    pages_to_show = list(range(max(current_page - 1, 1), min(current_page + 2, total_pages + 1)))
    if pages_to_show[0] > 1:
        if pages_to_show[0] > 2:
            pages_to_show.insert(0, '...')
        pages_to_show.insert(0, 1)
    if pages_to_show[-1] < total_pages:
        if pages_to_show[-1] < total_pages - 1:
            pages_to_show.append('...')
        pages_to_show.append(total_pages)

    context = {
        'content_type': content_type,
        'page_obj': page_obj,
        'pages_to_show': pages_to_show,
    }
    return render(request, 'movies/content_list.html', context)


def content_detail(request, content_id):
    content = get_object_or_404(Content, id=content_id)
    reviews = Review.objects.filter(content=content)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.content = content
            review.save()
            return redirect('movies:content_detail', content_id=content.id)
    else:
        form = ReviewForm()
    
    context = {
        'content': content,
        'reviews': reviews,
        'form': form,
    }
    return render(request, 'movies/content_detail.html', context)


def terms_of_service(request):
    return render(request, 'movies/terms_of_service.html')

def search(request):
    query = request.GET.get('query', '')
    movie_results = Content.objects.filter(type='movie', title__icontains=query)
    series_results = Content.objects.filter(type='series', title__icontains=query)
    music_results = Content.objects.filter(type='music', title__icontains=query)
    nollywood_results = Content.objects.filter(type='nollywood', title__icontains=query)
    context = {
        'query': query,
        'movie_results': movie_results,
        'series_results': series_results,
        'music_results': music_results,
        'nollywood_results': nollywood_results,

    }
    return render(request, 'movies/search_results.html', context)

def privacy_policy(request):
    return render(request, 'movies/privacy_policy.html')

def contact_us(request):
    return render(request, 'movies/contact_us.html')

def home(request):
    return redirect('content_list', content_type='movie')

def advertise_with_us(request):
    return render(request, 'movies/advertise.html')


def download_content(request, content_id):
    content = get_object_or_404(Content, id=content_id)

    if content.type == 'music':
        # Directly redirect to the permanent music file link
        return redirect(content.permanent_download_link)
    else:
        new_download_link = content.update_download_link()
        if new_download_link:
            return HttpResponseRedirect(new_download_link)
        else:
            return HttpResponseRedirect('/error-page')  # Redirect to an error page or a different page

def finalize_download(request, content_id):
    content = get_object_or_404(Content, id=content_id)
    
    if content.type != 'music':
        content.revert_to_permanent_link()
    
    return HttpResponseRedirect('/thank-you')  # Redirect to a thank-you page or elsewhere

@require_http_methods(["GET", "POST"])
def donate(request):
    if request.method == "POST":
        amount = request.POST.get('amount')
        email = request.POST.get('email')
        
        # You could save this information to a database or process it as needed
        
        return render(request, 'movies/donate.html', {'amount': amount, 'email': email})
    
    # Handle GET request
    return render(request, 'movies/donate.html')