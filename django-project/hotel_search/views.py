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
# def search_view(request):
#     if request.method == 'POST':
#         form = HotelSearchForm(request.POST)
#         if form.is_valid():
#             city = form.cleaned_data['city']
#             price_range = form.cleaned_data.get('price_range', '')
#             star_rating = form.cleaned_data.get('star_rating', '')

#             # Trigger celery task and get the group task ID
#             task = run_spiders_for_query.delay(city, price_range, star_rating)
            
#             context = {
#                 'form': form,
#                 'task_id': task.id
#             }
#             return render(request, 'hotels/search.html', context)
        
#         if city and price and rating:
#             # Call the Celery task asynchronously
#             task_result = run_spiders_for_query.delay(city, price, rating)
            
#             # Redirect to the results page, passing the group task_id
#             return redirect('hotel_results', task_id=task_result.id)
#     else:
#         form = HotelSearchForm()

#     return render(request, 'hotels/search.html', {'form': form})

# def poll_search_results(request, task_id):
#     """
#     API endpoint to be polled by JavaScript.
#     Returns the status of the task and the results found so far.
#     """
#     task = AsyncResult(task_id)
    
#     if task.ready():
#         # The group task is ready, which means subtasks are done.
#         # We can now fetch all hotels related to the subtask IDs.
#         # The result of the group task is a list of results of subtasks.
#         subtask_ids = task.get()
#         hotels = Hotel.objects.filter(search_task_id__in=subtask_ids).distinct()
        
#         # Check bookmarks for the current user
#         bookmarked_hotel_ids = []
#         if request.user.is_authenticated:
#             bookmarked_hotel_ids = list(Bookmark.objects.filter(user=request.user).values_list('hotel_id', flat=True))

#         return JsonResponse({
#             'status': 'SUCCESS',
#             'hotels': [{
#                 'id': h.id,
#                 'name': h.name,
#                 'location': h.location,
#                 'price': h.price,
#                 'rating': h.rating,
#                 'image_url': h.image_url,
#                 'hotel_url': h.hotel_url,
#                 'source': h.source,
#                 'is_bookmarked': h.id in bookmarked_hotel_ids
#             } for h in hotels]
#         })
#     else:
#         # Task is still running, let's fetch what we have so far
#         # This is a bit trickier with groups, we'll just report PENDING
#         return JsonResponse({'status': 'PENDING'})

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

import logging
# Get an instance of a logger (assuming this is defined at the top of views.py)
logger = logging.getLogger(__name__)


def poll_search_results(request, task_id):
    """
    API endpoint to be polled by JavaScript.
    Returns the status of the group task and ONLY the NEW results found by this specific task.
    """
    try:
        task = AsyncResult(str(task_id)) # Ensure task_id is string
        
        logger.info(f"Polling for task_id: {task_id}")
        logger.info(f"Task object type: {type(task)}")
        logger.info(f"Task status: {task.status}") # Log current status

        data = {
            'status': task.status,
            'progress': 'N/A',
            'error': None
        }

        if task.ready(): # Group task is ready (SUCCESS or FAILURE)
            all_subtask_results = []
            successful_subtask_ids = []
            failed_subtask_errors = []

            if task.children: # Check if the group task has children
                logger.info(f"Group task {task_id} has children. Fetching individual results.")
                for child_task_async_result in task.children:
                    try:
                        child_result = child_task_async_result.get(timeout=1) # Get the result of each child task

                        results_to_process = child_result if isinstance(child_result, list) else [child_result]

                        for res_item in results_to_process:
                            all_subtask_results.append(res_item) # Keep track of all results

                            # --- DEEPER DEBUGGING HERE ---
                            logger.info(f"Processing res_item: {res_item} (Type: {type(res_item)})")
                            if isinstance(res_item, dict):
                                logger.info(f"res_item is a dict. Keys: {res_item.keys()}")
                                if 'status' in res_item:
                                    logger.info(f"res_item has 'status' key. Value: {res_item['status']}")
                                    if res_item['status'] == 'SUCCESS':
                                        successful_subtask_ids.append(str(res_item['task_id']))
                                    elif res_item['status'] == 'FAILURE':
                                        if res_item.get('error'):
                                            failed_subtask_errors.append(res_item.get('error'))
                                    else:
                                        logger.warning(f"res_item status is not SUCCESS/FAILURE: {res_item['status']} for {child_task_async_result.id}")
                                        failed_subtask_errors.append(f"Unexpected status '{res_item['status']}' from subtask {child_task_async_result.id}")
                                else:
                                    logger.warning(f"res_item is a dict but missing 'status' key for {child_task_async_result.id}: {res_item}")
                                    failed_subtask_errors.append(f"Subtask {child_task_async_result.id} result missing 'status' key.")
                            else:
                                logger.warning(f"Unexpected item format within child result (NOT A DICT) for {child_task_async_result.id}: {res_item}")
                                failed_subtask_errors.append(f"Unexpected non-dict format from subtask {child_task_async_result.id}: {res_item}")
                            # --- END DEEPER DEBUGGING ---

                    except Exception as child_e:
                        logger.exception(f"Error getting result for child task {child_task_async_result.id}")
                        failed_subtask_errors.append(f"Error getting result from subtask {child_task_async_result.id}: {str(child_e)}")
            else:
                logger.warning(f"Group task {task_id} is ready but has no children. This is unexpected.")
                if task.status == 'FAILURE':
                    data['error'] = str(task.result)
                else:
                    data['error'] = "Group task completed without reporting child results."


            logger.info(f"----> All subtask results collected: {all_subtask_results}")
            logger.info(f"----> Successful subtask IDs: {successful_subtask_ids}")
            
            if successful_subtask_ids:
                new_hotels_queryset = Hotel.objects.filter(search_task_id=str(task_id)).distinct().order_by('-created_at')
            else:
                new_hotels_queryset = Hotel.objects.none()

            logger.info(f"===> Hotels found in DB for task_id {task_id}: {new_hotels_queryset.count()}")

            bookmarked_hotel_ids = []
            if request.user.is_authenticated:
                bookmarked_hotel_ids = list(Bookmark.objects.filter(user=request.user).values_list('hotel_id', flat=True))

            data['status'] = 'SUCCESS'
            data['hotels'] = [{
                'id': h.id,
                'name': h.name,
                'location': h.location,
                'price': h.price,
                'rating': h.rating,
                'image_url': h.image_url,
                'hotel_url': h.hotel_url,
                'source': h.source,
                'is_bookmarked': h.id in bookmarked_hotel_ids
            } for h in new_hotels_queryset]

            if failed_subtask_errors:
                data['error'] = "Some spiders failed: " + "; ".join(failed_subtask_errors)

        elif task.status == 'FAILURE':
            data['error'] = str(task.result)
        
        return JsonResponse(data)
    except Exception as e:
        logger.exception(f"Unexpected error in poll_search_results for task_id: {task_id}")
        return JsonResponse({
            'status': 'FAILURE',
            'error': f"An unexpected server error occurred: {str(e)}"
        }, status=500)


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
