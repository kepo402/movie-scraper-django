from django import template

register = template.Library()

@register.simple_tag
def render_stars(rating):
    print(f"Rendering stars for rating: {rating}")  # For debugging
    stars = ''
    for i in range(1, 6):
        if i <= rating:
            stars += '★'
        else:
            stars += '☆'
    return stars

