from django.urls import path
from . import views
from .views import CustomLoginView, register_view, logout_any

urlpatterns = [
    # path('', views.search_view, name='search'),
    # path('search/', views.search_view, name='search'),
    
    # path('results/poll/<str:task_id>/', views.poll_search_results, name='poll_results'),
    # path('bookmark/toggle/<int:hotel_id>/', views.toggle_bookmark_view, name='toggle_bookmark'),
    # path('bookmarks/', views.bookmark_list_view, name='bookmark_list'),
    
    path('', views.search_hotels_view, name='search_hotels'),
    path('search/', views.search_hotels_view, name='search_hotels'),
    path('results/', views.hotel_results_view, name='hotel_results_all'), # NEW: For viewing all results
    path('results/<uuid:task_id>/', views.hotel_results_view, name='hotel_results'),
    path('status/<uuid:task_id>/', views.poll_search_results, name='poll_search_results'), # Polling endpoint
    # path('bookmark/toggle/<int:hotel_id>/', views.toggle_bookmark, name='toggle_bookmark'), # Bookmark endpoint
    
    
    path('login/', CustomLoginView.as_view(), name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', logout_any, name='logout'),
]