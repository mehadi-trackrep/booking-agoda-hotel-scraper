# scraper/scraper/spiders/agoda_spider.py

import scrapy
from urllib.parse import urlencode, urljoin
from ..items import ScraperItem # Assuming ScraperItem is defined in scraper/scraper/items.py

class AgodaSpider(scrapy.Spider):
    name = 'agoda_spider'
    
    # Base URL for Agoda.com search results
    # Agoda's URLs can be quite dynamic, this is a simplified example.
    base_search_url = 'https://www.agoda.com/search' 

    def __init__(self, city=None, price=None, rating=None, task_id=None, *args, **kwargs):
        super(AgodaSpider, self).__init__(*args, **kwargs)
        self.city = city
        self.price = price
        self.rating = rating
        self.task_id = task_id # Celery task ID for tracking

        if not self.city:
            raise ValueError("City argument is required for agoda_spider.")

        # Construct initial URL parameters for Agoda
        # Agoda often uses a destination ID or a more complex search endpoint.
        # You MUST investigate Agoda.com's search process in your browser's
        # network tab to find the correct parameters.
        params = {'city': self.city} # Placeholder, likely needs more specific Agoda params

        # --- IMPORTANT: Price and Rating Filtering ---
        # Agoda's filtering is also complex and often uses:
        # 1. Specific URL parameters (e.g., 'price_range=low-high', 'star_rating=4')
        # 2. JavaScript-driven filters.
        # You MUST inspect Agoda.com's network requests when applying these filters
        # manually to find the correct parameters and their values.
        if self.price:
            # Example: You might need to map '100-200' to Agoda's specific filter
            # params['price_range'] = self.map_price_to_agoda_filter(self.price)
            self.logger.info(f"Price filter '{self.price}' provided, but might require specific Agoda.com URL parameter mapping.")
        if self.rating:
            # Example: You might need to map '4+' to Agoda's star rating filter
            # params['star_rating'] = self.map_rating_to_agoda_filter(self.rating)
            self.logger.info(f"Rating filter '{self.rating}' provided, but might require specific Agoda.com URL parameter mapping.")

        self.start_urls = [f'{self.base_search_url}?{urlencode(params)}']
        self.logger.info(f"Starting spider '{self.name}' for city: '{self.city}', task_id: '{self.task_id}'")
        self.logger.info(f"Initial URL: {self.start_urls[0]}")

    # Helper function for price mapping (conceptual)
    def map_price_to_agoda_filter(self, price_str):
        # Implement logic to convert '100-200' to Agoda's internal price filter
        return price_str # Placeholder

    # Helper function for rating mapping (conceptual)
    def map_rating_to_agoda_filter(self, rating_str):
        # Implement logic to convert '4+' to Agoda's internal rating filter (e.g., star rating)
        return rating_str # Placeholder

    def parse(self, response):
        """
        Parses the search results page.
        IMPORTANT: These selectors are examples and WILL break. You must inspect
        Agoda.com and update them to match the current site structure.
        """
        self.logger.info(f"Parsing URL: {response.url}")
        
        # Agoda often uses JavaScript to load content, so direct CSS selectors
        # might not work for all data. You might need Scrapy-Playwright/Selenium.
        # However, for basic HTML, try these example selectors (LIKELY OUTDATED - VERIFY ON LIVE SITE)
        hotel_cards = response.css('div[data-selenium="hotel-item"]') # Common container for hotel listings

        if not hotel_cards:
            self.logger.warning(f"No hotel cards found on {response.url}. Selectors might be outdated or no results.")
            self.logger.warning("Agoda often loads content via JavaScript. Consider using Scrapy-Playwright or Scrapy-Selenium.")

        for card in hotel_cards:
            item = ScraperItem()
            item['search_task_id'] = self.task_id # Pass the Celery task ID
            item['source'] = self.name # 'agoda_spider'

            # Extract data using CSS selectors
            # Verify these selectors on the live Agoda.com website!
            item['name'] = card.css('h3[data-selenium="hotel-header"]::text').get()
            item['location'] = card.css('span[data-selenium="area-name"]::text').get()
            
            # Price extraction can be tricky. Look for final price.
            item['price'] = card.css('div[data-selenium="price-text"]::text').get()
            
            # Rating might be a star rating or a score.
            item['rating'] = card.css('div[data-selenium="review-score"]::text').get() or \
                             card.css('i.star-rating::attr(aria-label)').get() # Example for star icons
            
            item['image_url'] = card.css('img[data-selenium="hotel-image"]::attr(src)').get()
            
            # Ensure the URL is absolute
            hotel_relative_url = card.css('a[data-selenium="hotel-item-link"]::attr(href)').get()
            if hotel_relative_url:
                item['hotel_url'] = urljoin(response.url, hotel_relative_url)
            else:
                item['hotel_url'] = None

            yield item

        # --- Pagination (Crucial for scraping multiple pages) ---
        # Agoda's pagination is often JavaScript-driven. You might need to
        # simulate clicks or find API calls. This is a basic example.
        next_page_link = response.css('a[data-selenium="pagination-next-button"]::attr(href)').get()
        if next_page_link:
            next_page_url = response.urljoin(next_page_link)
            self.logger.info(f"Following next page link: {next_page_url}")
            yield scrapy.Request(url=next_page_url, callback=self.parse)
        else:
            self.logger.info(f"No next page link found on {response.url}. Finished scraping.")

