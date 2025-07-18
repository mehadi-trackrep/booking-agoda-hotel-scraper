import re
import scrapy
from urllib.parse import urlencode, urljoin
from ..items import ScraperItem
from scrapy.selector import Selector
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
                # callback=self.parse,
                callback=self.parse_with_mock_data,
            )

    def parse_with_mock_data(self, response):
        hotels = [
            {
                'name': 'City View Hotel Roman Road',
                'location': 'Tower Hamlets, London',
                'price': '55',
                'rating': '4.0',
                'image_url': 'https://pix8.agoda.net/hotelImages/175493/0/63c73abe66efd568b94652bcba66c332.jpeg?s=1024x',
                'hotel_url': 'https://www.agoda.com/en-gb/city-view-hotel-roman-road/hotel/london-gb.html?countryId=107&finalPriceView=1&isShowMobileAppPrice=false&cid=-1&numberOfBedrooms=&familyMode=false&adults=1&children=0&rooms=1&maxRooms=0&checkIn=2025-07-18&isCalendarCallout=false&childAges=&numberOfGuest=0&missingChildAges=false&travellerType=-1&showReviewSubmissionEntry=false&currencyCode=USD&isFreeOccSearch=false&tspTypes=9&los=1&searchrequestid=15db6227-ca60-486d-8ed6-f115ea1580a2',
            },
            {
                'name': 'Safestay London Kensington Holland Park',
                'location': 'Chelsea, London',
                'price': '12',
                'rating': '2.0',
                'image_url': 'https://pix8.agoda.net/hotelImages/908/908614/908614_16030423280040480274.jpg?ca=6&ce=1&s=1024x',
                'hotel_url': 'https://www.agoda.com/en-gb/safestay-london-kensington-holland-park/hotel/london-gb.html?countryId=107&finalPriceView=1&isShowMobileAppPrice=false&cid=-1&numberOfBedrooms=&familyMode=false&adults=1&children=0&rooms=1&maxRooms=0&checkIn=2025-07-18&isCalendarCallout=false&childAges=&numberOfGuest=0&missingChildAges=false&travellerType=-1&showReviewSubmissionEntry=false&currencyCode=USD&isFreeOccSearch=false&los=1&searchrequestid=15db6227-ca60-486d-8ed6-f115ea1580a2',
            },
            {
                'name': 'Hilton London Hyde Park',
                'location': 'Kensington and Chelsea, London',
                'price': '50',
                'rating': '3.0',
                'image_url': 'https://cf.bstatic.com/xdata/images/hotel/max1024x768/483770904.jpg?k=2f395dea9ee949adb81859453863fb4a10809448e6f00c7d79c008505f0502a3&o=',
                'hotel_url': 'https://www.booking.com/hotel/gb/hilton-london-hyde-park.en-gb.html?aid=304142&label=gen173nr-1FCAQoggJCDXNlYXJjaF9sb25kb25IM1gEaBSIAQGYAQm4ARfIAQzYAQHoAQH4AQOIAgGoAgO4AsSb58MGwAIB0gIkMjMxODM3YjMtZTFmNC00OTMzLWE2NTUtZjc3MmM4Zjc0NTFk2AIF4AIB&sid=ab2da25220b03532e0825e02d48f1b7c&all_sr_blocks=3558007_244917320_2_34_0&checkin=2025-07-18&checkout=2025-07-20&dest_id=-2601889&dest_type=city&dist=0&group_adults=2&group_children=0&hapos=1&highlighted_blocks=3558007_244917320_2_34_0&hpos=1&matching_block_id=3558007_244917320_2_34_0&no_rooms=1&req_adults=2&req_children=0&room1=A%2CA&sb_price_type=total&show_room=3558007&sr_order=popularity&sr_pri_blocks=3558007_244917320_2_34_0__48100&srepoch=1752813135&srpvid=89eb1fe653c003eb&type=total&ucfs=1&#RD3558007',
            },
        ]
        self.logger.info(f"Found {len(hotels)} hotels on page: {response.url}")
        
        for hotel in hotels:
            item = ScraperItem()
            item['search_task_id'] = self.search_task_id
            item['source'] = self.name

            item['name'] = hotel['name']
            item['location'] = hotel['location']
            item['price'] = hotel['price']
            item['rating'] = hotel['rating']
            item['image_url'] = hotel['image_url']
            item['hotel_url'] = hotel['hotel_url']
            
            yield item

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
            
            # self.logger.info(f"-=-=-=> card: {card}")
            
            
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
            item['rating'] = str(card.css('div[data-testid="review-score"] div::text').get()).replace('Scored', '').strip()
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

