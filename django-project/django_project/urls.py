from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', include('hotel_search.urls')),
    path('hotels/', include('hotel_search.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]