from hotel_search.models import Hotel 
from itemadapter import ItemAdapter # Recommended for accessing item fields
from asgiref.sync import sync_to_async # Import sync_to_async

class HotelScraperPipeline:
    # Scrapy pipelines can be synchronous, but if they interact with Django's ORM
    # in an asynchronous environment (like when Scrapy is run via Celery, or in some
    # advanced Scrapy setups), you need to handle synchronous operations.
    # The 'SynchronousOnlyOperation' error indicates that Django's ORM is being
    # called from an async context. We use sync_to_async to wrap these calls.

    async def process_item(self, item, spider): # Make process_item an async function
        """
        Processes each scraped item.
        Saves or updates hotel data in the Django database.
        """
        adapter = ItemAdapter(item) # Use ItemAdapter for robust field access

        # Extract required fields for update_or_create
        name = adapter.get('name')
        location = adapter.get('location')
        source = adapter.get('source')
        search_task_id = adapter.get('search_task_id') # Celery task ID

        # Ensure essential fields are present
        if not name or not location or not source:
            spider.logger.warning(f"Skipping item due to missing essential fields: {item}")
            return item # Return item so it can be processed by other pipelines if any

        # Use update_or_create to handle hotels found by different searches
        # or to update details if found again.
        # The 'defaults' dictionary contains fields that should be updated
        # if the object already exists, or set if a new object is created.
        try:
            # Wrap the synchronous ORM call with sync_to_async
            hotel, created = await sync_to_async(Hotel.objects.update_or_create)(
                # Fields used to identify an existing record
                name=name,
                location=location,
                source=source,
                defaults={
                    # Fields to set/update
                    'search_task_id': search_task_id,
                    'price': adapter.get('price'),
                    'rating': adapter.get('rating'),
                    'image_url': adapter.get('image_url'),
                    'hotel_url': adapter.get('hotel_url'),
                }
            )
            if created:
                spider.logger.info(f"Created new hotel entry: {hotel.name} from {hotel.source}")
            else:
                spider.logger.info(f"Updated existing hotel entry: {hotel.name} from {hotel.source}")
        except Exception as e:
            spider.logger.error(f"Error saving hotel item to Django DB: {e} for item: {item}")
            # Depending on your needs, you might want to re-raise the exception
            # or simply log it and continue. For now, we log and return the item.
        
        return item # Always return the item to pass it to the next pipeline (if any)
