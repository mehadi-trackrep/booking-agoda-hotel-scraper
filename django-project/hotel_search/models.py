from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

class Customer(AbstractUser):
    email = models.EmailField(unique=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.username


class Hotel(models.Model):
    """
    Stores individual hotel data scraped from a source.
    """
    search_task_id = models.CharField(max_length=255, help_text="Celery task ID for the search")
    name = models.CharField(max_length=512)
    location = models.CharField(max_length=512, null=True, blank=True)
    price = models.CharField(max_length=100, null=True, blank=True)
    rating = models.CharField(max_length=50, null=True, blank=True)
    image_url = models.URLField(max_length=2048, null=True, blank=True)
    hotel_url = models.URLField(max_length=2048, null=True, blank=True)
    source = models.CharField(max_length=100) # e.g., 'Booking.com', 'Agoda'
    scraped_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} from {self.source}"

    class Meta:
        ordering = ['-scraped_at']
        unique_together = ('name', 'location', 'source')
        app_label = 'hotel_search'

class Bookmark(models.Model):
    """
    Connects a user to a bookmarked hotel.
    """
    user = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='bookmarks')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='bookmarked_by')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} bookmarked {self.hotel.name}"

    class Meta:
        unique_together = ('user', 'hotel')
        app_label = 'hotel_search'