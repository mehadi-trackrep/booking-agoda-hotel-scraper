# scraper/scraper/spiders/booking_spider.py

import scrapy
from urllib.parse import urlencode, urljoin
from ..items import ScraperItem # Assuming ScraperItem is defined in scraper/scraper/items.py

class BookingSpider(scrapy.Spider):
    name = 'booking_spider'
    
    # Base URL for Booking.com search results
    base_search_url = 'https://www.booking.com/searchresults.html'

    def __init__(self, city=None, price=None, rating=None, search_task_id=None, *args, **kwargs):
        super(BookingSpider, self).__init__(*args, **kwargs)
        self.city = city
        self.price = price
        self.rating = rating
        self.search_task_id = search_task_id # Celery task ID for tracking

        if not self.city:
            raise ValueError("City argument is required for booking_spider.")

        # Construct initial URL parameters
        params = {'ss': self.city} # 'ss' is typically the destination query parameter

        # --- IMPORTANT: Price and Rating Filtering ---
        # Booking.com's filtering for price and rating is complex and often uses:
        # 1. Specific URL parameters (e.g., 'price_range=low-high', 'review_score=90')
        # 2. JavaScript-driven filters that are harder to replicate in initial URL
        # You MUST inspect Booking.com's network requests when applying these filters
        # manually to find the correct parameters and their values.
        # For now, this is a placeholder.
        if self.price:
            # Example: You might need to map '100-200' to a specific Booking.com filter value
            # params['price_range'] = self.map_price_to_booking_filter(self.price)
            self.logger.info(f"Price filter '{self.price}' provided, but might require specific Booking.com URL parameter mapping.")
        if self.rating:
            # Example: You might need to map '4+' to a specific Booking.com review score filter
            # params['review_score'] = self.map_rating_to_booking_filter(self.rating)
            self.logger.info(f"Rating filter '{self.rating}' provided, but might require specific Booking.com URL parameter mapping.")

        self.start_urls = [f'{self.base_search_url}?{urlencode(params)}']
        self.logger.info(f"Starting spider '{self.name}' for city: '{self.city}', task_id: '{self.search_task_id}'")
        self.logger.info(f"Initial URL: {self.start_urls[0]}")

    # Helper function for price mapping (conceptual)
    def map_price_to_booking_filter(self, price_str):
        # Implement logic to convert '100-200' to Booking.com's internal price filter
        # e.g., return 'price_range_1' or similar
        return price_str # Placeholder

    # Helper function for rating mapping (conceptual)
    def map_rating_to_booking_filter(self, rating_str):
        # Implement logic to convert '4+' to Booking.com's internal rating filter
        # e.g., return 'review_score_90' for 9+ or similar
        return rating_str # Placeholder

    def parse(self, response):
        """
        Parses the search results page.
        IMPORTANT: These selectors are examples and WILL break. You must inspect
        booking.com and update them to match the current site structure.
        """
        self.logger.info(f"Parsing URL: {response.url}")
        
        # Selectors are highly prone to change. Use your browser's developer tools
        # (Inspect Element) to find the correct, current selectors for Booking.com.
        # Look for unique data attributes (like data-testid) or stable class names.
        
        # Example selectors (LIKELY OUTDATED - VERIFY ON LIVE SITE)
        hotel_cards = response.css('div[data-testid="property-card"]') # Common container for hotel listings

        if not hotel_cards:
            self.logger.warning(f"No hotel cards found on {response.url}. Selectors might be outdated or no results.")

        for card in hotel_cards:
            item = ScraperItem()
            item['search_task_id'] = self.search_task_id # Pass the Celery task ID
            item['source'] = self.name # 'booking_spider'

            # Extract data using CSS selectors
            # Verify these selectors on the live Booking.com website!
            item['name'] = card.css('div[data-testid="title"]::text').get()
            item['location'] = card.css('span[data-testid="address"]::text').get()
            
            # Price extraction can be tricky due to formatting, discounts, etc.
            # You might need more complex logic or regex here.
            item['price'] = card.css('span[data-testid="price-and-discounted-price"]::text').get() or \
                            card.css('span.prco-valign-top::text').get() # Another common price selector

            # Rating often involves multiple elements. You might need to combine text or extract attributes.
            item['rating'] = card.css('div[data-testid="review-score"] div::text').get() or \
                             card.css('div.bui-review-score__badge::text').get()
            
            item['image_url'] = card.css('img[data-testid="image"]::attr(src)').get()
            
            # Ensure the URL is absolute
            hotel_relative_url = card.css('a[data-testid="title-link"]::attr(href)').get()
            if hotel_relative_url:
                item['hotel_url'] = urljoin(response.url, hotel_relative_url)
            else:
                item['hotel_url'] = None # Or handle as error

            yield item

        # --- Pagination (Crucial for scraping multiple pages) ---
        # Find the next page link. This selector is also highly prone to change.
        next_page_link = response.css('a[data-testid="pagination-page-next"]::attr(href)').get()
        if next_page_link:
            next_page_url = response.urljoin(next_page_link)
            self.logger.info(f"Following next page link: {next_page_url}")
            yield scrapy.Request(url=next_page_url, callback=self.parse)
        else:
            self.logger.info(f"No next page link found on {response.url}. Finished scraping.")

