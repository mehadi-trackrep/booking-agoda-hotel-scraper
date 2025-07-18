import re
import scrapy
from urllib.parse import urlencode, urljoin
from ..items import ScraperItem
from scrapy_playwright.page import PageMethod

class BookingSpider(scrapy.Spider):
    name = 'booking_spider'
    
    base_search_url = 'https://www.booking.com/searchresults.html'

    def __init__(self, city=None, price=None, rating=None, checkin=None, search_task_id=None, *args, **kwargs):
        super(BookingSpider, self).__init__(*args, **kwargs)
        self.city = city
        self.price = price
        self.rating = rating
        self.checkin = checkin
        self.search_task_id = search_task_id

        if not self.city:
            raise ValueError("City argument is required for booking_spider.")

        params = {'ss': self.city, 'checkin': self.checkin}

        self.start_urls = [f'{self.base_search_url}?{urlencode(params)}']
        self.logger.info(f"Starting spider '{self.name}' for city: '{self.city}', task_id: '{self.search_task_id}'")
        self.logger.info(f"Initial URL: {self.start_urls[0]}")

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                # meta={
                #     "playwright": True,
                #     "playwright_page_methods": [
                #         PageMethod("wait_for_selector", 'div[data-testid="property-card"]'),
                #     ],
                # },
                callback=self.parse,
            )

    def parse(self, response):
        """
        Parses the search results page.
        """
        self.logger.info(f"Parsing URL: {response.url}")
        
        hotel_cards = response.css('div[data-testid="property-card"]')

        if not hotel_cards:
            self.logger.warning(f"No hotel cards found on {response.url}. Selectors might be outdated or no results.")

        for card in hotel_cards:
            item = ScraperItem()
            item['search_task_id'] = self.search_task_id
            item['source'] = self.name
            
            price_text = card.css('span[data-testid="price-and-discounted-price"]::text').get()
            self.logger.info(f"==> price: {price_text}")
            
            if price_text:
                # Remove everything except digits
                price_numeric = re.sub(r"[^\d]", "", price_text)
                if price_numeric:
                    price_numeric = int(price_numeric)  # Convert to integer
                else:
                    price_numeric = None
            else:
                price_numeric = None

            item['price'] = price_numeric
            
            item['name'] = card.css('div[data-testid="title"]::text').get()
            item['location'] = card.css('span[data-testid="address"]::text').get()
            # item['price'] = card.css('span[data-testid="price-and-discounted-price"]::text').get()
            item['rating'] = card.css('div[data-testid="review-score"] div::text').get()
            item['image_url'] = card.css('img[data-testid="image"]::attr(src)').get()
            
            hotel_relative_url = card.css('a[data-testid="title-link"]::attr(href)').get()
            if hotel_relative_url:
                item['hotel_url'] = urljoin(response.url, hotel_relative_url)
            else:
                item['hotel_url'] = None

            yield item

        next_page_link = response.css('a[data-testid="pagination-page-next"]::attr(href)').get()
        if next_page_link:
            next_page_url = response.urljoin(next_page_link)
            self.logger.info(f"Following next page link: {next_page_url}")
            yield scrapy.Request(
                next_page_url,
                # meta={
                #     "playwright": True,
                #     "playwright_page_methods": [
                #         PageMethod("wait_for_selector", 'div[data-testid="property-card"]'),
                #     ],
                # },
                callback=self.parse,
            )
        else:
            self.logger.info(f"No next page link found on {response.url}. Finished scraping.")

