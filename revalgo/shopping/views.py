from django.shortcuts import render

# Create your views here.

def index(request):
    """
    Render the index page of the shopping app.
    
    Args:
        request: The HTTP request object.
    
    Returns:
        HttpResponse: Rendered index page.
    """
    return render(request, 'shopping/index.html')

def recommendations(request):
    return render(request, 'shopping/recommendations.html')
