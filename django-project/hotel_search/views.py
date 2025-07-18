import os
import requests
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Bookmark
from loguru import logger as LOGGER
from django.conf import settings
from .forms import RegisterForm, LoginForm
from django.contrib.auth.views import LoginView
from .mock_data import MockDataGenerator


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.save()
            login(request, user)
            return redirect('search')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


class CustomLoginView(LoginView):
    authentication_form = LoginForm
    template_name = "registration/login.html"

@login_required
def remove_bookmark(request, pk):
    Bookmark.objects.filter(id=pk, user=request.user).delete()
    return redirect('bookmarks')

from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET", "POST"])
def logout_any(request):
    logout(request)
    return redirect('login')


### ------------------------------------------  ###
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import HotelSearchForm
from .tasks import run_spiders_for_query
from .models import Hotel, Bookmark
from celery.result import AsyncResult


# @login_required
# def toggle_bookmark_view(request, hotel_id):
#     if request.method == 'POST':
#         hotel = get_object_or_404(Hotel, id=hotel_id)
#         bookmark, created = Bookmark.objects.get_or_create(user=request.user, hotel=hotel)
        
#         if not created:
#             # If bookmark already existed, remove it
#             bookmark.delete()
#             return JsonResponse({'status': 'removed'})
#         else:
#             # If it was just created
#             return JsonResponse({'status': 'added'})
#     return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

# @login_required
# def bookmark_list_view(request):
#     bookmarks = Bookmark.objects.filter(user=request.user).select_related('hotel')
#     return render(request, 'hotels/bookmarks.html', {'bookmarks': bookmarks})


def search_hotels_view(request):
    """
    Handles the search form submission, initiates the Celery task,
    and redirects to the results page with the task ID.
    """
    if request.method == 'POST':
        city = request.POST.get('city')
        price = request.POST.get('price')
        rating = request.POST.get('rating')

        if city and price and rating:
            # Call the Celery task asynchronously
            task_result = run_spiders_for_query.delay(city, price, rating)
            
            # Redirect to the results page, passing the group task_id
            return redirect('hotel_results', task_id=task_result.id)
        else:
            return JsonResponse({'status': 'Missing parameters'}, status=400)
    return render(request, 'hotels/search.html') # Render your search form


def hotel_results_view(request, task_id=None): # <--- Make task_id optional
    """
    View to display scraped hotel results.
    Filters by task_id if provided, otherwise shows all.
    """
    hotels = Hotel.objects.all().order_by('-id') # Start with all hotels

    if task_id: # If a task_id is provided, filter by it
        # In your polling view, you get subtask_ids. Here, we're just filtering by the main group task_id
        # This means the `search_task_id` in your Hotel model should store the GROUP task_id,
        # not the individual spider task_id if you want to filter this way.
        # If `search_task_id` in Hotel model stores individual spider task IDs, you'd need a different approach here.
        # For simplicity, let's assume you want to filter by the main group task_id for this view.
        # If your Hotel model stores individual spider task IDs, you'd need to adjust this filter.
        # For now, let's assume `search_task_id` in Hotel model stores the GROUP task_id.
        hotels = hotels.filter(search_task_id=task_id)

    context = {
        'hotels': hotels,
        'task_id': task_id # Pass task_id to template if needed
    }
    return render(request, 'hotels/results.html', context)


def poll_search_results(request, task_id):
    """
    API endpoint to be polled by JavaScript.
    Returns the task status and any results found so far, allowing for real-time updates.
    """
    LOGGER.info(f"Polling for task_id: {task_id}")
    task = AsyncResult(str(task_id))

    # Always query for hotels found so far for this task.
    hotels_queryset = Hotel.objects.filter(search_task_id=str(task_id)).distinct().order_by('-scraped_at')
    
    bookmarked_hotel_ids = []
    if request.user.is_authenticated:
        bookmarked_hotel_ids = list(Bookmark.objects.filter(user=request.user).values_list('hotel_id', flat=True))

    hotels_data = [{
        'id': h.id, 'name': h.name, 'location': h.location, 'price': h.price,
        'rating': h.rating, 'image_url': h.image_url, 'hotel_url': h.hotel_url,
        'source': h.source, 'is_bookmarked': h.id in bookmarked_hotel_ids
    } for h in hotels_queryset]
    
    LOGGER.info(f"Found {len(hotels_data)} hotels in DB for task {task_id}. Task status: {task.status}")

    error_message = None
    # Check for failures specifically.
    if task.status == 'FAILURE':
        error_message = "A task failed."
        # If there are children, try to find the specific error.
        if task.children:
            failed_child_errors = []
            for child in task.children:
                if child.failed():
                    # The result of the failed child task contains the error info
                    try:
                        child_result = child.get() # this should not block if child.failed() is true
                    except Exception as e:
                        child_result = str(e)

                    # The individual_spider_task returns a dict on failure
                    if isinstance(child_result, dict) and 'error' in child_result:
                        failed_child_errors.append(child_result['error'])
                    else:
                        failed_child_errors.append(str(child_result))
            if failed_child_errors:
                error_message = "Some spiders failed: " + "; ".join(failed_child_errors)
        else:
            error_message = f"Task failed: {task.result}"

    return JsonResponse({
        'status': task.status,
        'hotels': hotels_data,
        'error': error_message,
    })


@login_required
def toggle_bookmark(request, hotel_id):
    """
    API endpoint to toggle (add/remove) a hotel from user's bookmarks.
    """
    hotel = get_object_or_404(Hotel, id=hotel_id)
    user = request.user

    bookmarked = False
    try:
        bookmark = Bookmark.objects.get(user=user, hotel=hotel)
        bookmark.delete()
        status = 'removed'
    except Bookmark.DoesNotExist:
        Bookmark.objects.create(user=user, hotel=hotel)
        status = 'added'
        bookmarked = True
    
    return JsonResponse({'status': status, 'is_bookmarked': bookmarked})
