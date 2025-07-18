# scraper/scraper/spiders/agoda_spider.py

import scrapy
from urllib.parse import urlencode, urljoin
from ..items import ScraperItem
from loguru import logger as LOGGER
from scrapy_crawlbase.request import CrawlbaseRequest
from scrapy_playwright.page import PageMethod

class AgodaSpider(scrapy.Spider):
    name = 'agoda_spider'
    
    # custom_settings = {
    #     'CRAWLBASE_ENABLED': True,
    #     'CRAWLBASE_TOKEN': 'your token',
    #     'DOWNLOADER_MIDDLEWARES': {
    #         'scrapy_crawlbase.CrawlbaseMiddleware': 610
    #     }
    # }
    
    base_search_url = 'https://www.agoda.com/en-gb/search'

    def __init__(self, city=None, price=None, rating=None, checkin=None, agoda_city_id=None, search_task_id=None, *args, **kwargs):
        super(AgodaSpider, self).__init__(*args, **kwargs)
        self.city = city
        self.price = price
        self.rating = rating
        self.checkin = checkin
        self.agoda_city_id = agoda_city_id
        self.search_task_id = search_task_id

        if not self.city:
            raise ValueError("City argument is required for agoda_spider.")

        params = {
            'city': self.agoda_city_id,
            'priceFrom': self.price,
            'priceTo': self.price,
            'hotelStarRating': rating,
            'textToSearch': self.city,
            'checkIn': self.checkin,
            # 'rooms': 1,
            # 'children': 0,
            'currencyCode': 'USD',
        }

        self.start_urls = [f'{self.base_search_url}?{urlencode({k: v for k, v in params.items() if v is not None})}']
        self.logger.info(f"Starting spider '{self.name}' for city: '{self.city}', search_task_id: '{self.search_task_id}'")
        self.logger.info(f"Initial URL: {self.start_urls[0]}")

    def start_requests(self):
        for url in self.start_urls:
            # yield CrawlbaseRequest(
            #     url,
            #     callback=self.parse,
            #     device='desktop',
            #     country='US',
            #     page_wait=1000,
            #     ajax_wait=True,
            #     dont_filter=True,
            # )
            
            yield scrapy.Request(
                url,
                # meta={
                #     "playwright": True,
                #     "playwright_page_methods": [
                #         PageMethod("wait_for_selector", "div.PropertyCardItem"),
                #     ],
                # },
                # callback=self.parse,  ## TODO INFO: Uncomment!
                callback=self.parse_mock_data, ## TODO INFO: Comment!
            )

    def parse_mock_data(self, response):
        hotels = [
            {
                'name': 'City View Hotel Roman Road',
                'location': 'Tower Hamlets, London - 1.1 km to center',
                'price': '53',
                'rating': '2.0',
                'image_url': 'https://pix8.agoda.net/hotelImages/175493/0/63c73abe66efd568b94652bcba66c332.jpeg?s=1024x',
                'hotel_url': 'https://www.agoda.com/en-gb/city-view-hotel-roman-road/hotel/london-gb.html?countryId=107&finalPriceView=1&isShowMobileAppPrice=false&cid=-1&numberOfBedrooms=&familyMode=false&adults=1&children=0&rooms=1&maxRooms=0&checkIn=2025-07-18&isCalendarCallout=false&childAges=&numberOfGuest=0&missingChildAges=false&travellerType=-1&showReviewSubmissionEntry=false&currencyCode=USD&isFreeOccSearch=false&tspTypes=9&los=1&searchrequestid=15db6227-ca60-486d-8ed6-f115ea1580a2',
            },
            {
                'name': 'Safestay London Kensington Holland Park',
                'location': 'Chelsea, London - 68 m to center',
                'price': '18',
                'rating': '3.0',
                'image_url': 'https://pix8.agoda.net/hotelImages/908/908614/908614_16030423280040480274.jpg?ca=6&ce=1&s=1024x',
                'hotel_url': 'https://www.agoda.com/en-gb/safestay-london-kensington-holland-park/hotel/london-gb.html?countryId=107&finalPriceView=1&isShowMobileAppPrice=false&cid=-1&numberOfBedrooms=&familyMode=false&adults=1&children=0&rooms=1&maxRooms=0&checkIn=2025-07-18&isCalendarCallout=false&childAges=&numberOfGuest=0&missingChildAges=false&travellerType=-1&showReviewSubmissionEntry=false&currencyCode=USD&isFreeOccSearch=false&los=1&searchrequestid=15db6227-ca60-486d-8ed6-f115ea1580a2',
            },
            {
                'name': 'Hilton London Hyde Park',
                'location': 'Kensington and Chelsea, London',
                'price': '53',
                'rating': '3.0',
                'image_url': 'https://cf.bstatic.com/xdata/images/hotel/max1024x768/483770904.jpg?k=2f395dea9ee949adb81859453863fb4a10809448e6f00c7d79c008505f0502a3&o=',
                'hotel_url': 'https://www.booking.com/hotel/gb/hilton-london-hyde-park.en-gb.html?aid=304142&label=gen173nr-1FCAQoggJCDXNlYXJjaF9sb25kb25IM1gEaBSIAQGYAQm4ARfIAQzYAQHoAQH4AQOIAgGoAgO4AsSb58MGwAIB0gIkMjMxODM3YjMtZTFmNC00OTMzLWE2NTUtZjc3MmM4Zjc0NTFk2AIF4AIB&sid=ab2da25220b03532e0825e02d48f1b7c&all_sr_blocks=3558007_244917320_2_34_0&checkin=2025-07-18&checkout=2025-07-20&dest_id=-2601889&dest_type=city&dist=0&group_adults=2&group_children=0&hapos=1&highlighted_blocks=3558007_244917320_2_34_0&hpos=1&matching_block_id=3558007_244917320_2_34_0&no_rooms=1&req_adults=2&req_children=0&room1=A%2CA&sb_price_type=total&show_room=3558007&sr_order=popularity&sr_pri_blocks=3558007_244917320_2_34_0__48100&srepoch=1752813135&srpvid=89eb1fe653c003eb&type=total&ucfs=1&#RD3558007',
            },
        ]
        LOGGER.info(f"Found {len(hotels)} hotels on page: {response.url}")
        
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


    def parse_old(self, response):
        """
        Parses the search results page.
        """
        self.logger.info(f"Parsing URL: {response.url}")
        
        hotel_cards = response.css('div.PropertyCardItem')

        if not hotel_cards:
            self.logger.warning(f"No hotel cards found on {response.url}. Selectors might be outdated or no results.")

        for card in hotel_cards:
            item = ScraperItem()
            item['search_task_id'] = self.search_task_id
            item['source'] = self.name

            item['name'] = card.css('h3[data-cy="hotel-name"]::text').get()
            item['location'] = card.css('span[data-cy="hotel-location"]::text').get()
            item['price'] = card.css('span[data-cy="price-display"]::text').get()
            item['rating'] = card.css('p[data-cy="hotel-rating"]::text').get()
            item['image_url'] = card.css('img[data-cy="hotel-image"]::attr(src)').get()
            
            hotel_relative_url = card.css('a.PropertyCard__Link::attr(href)').get()
            if hotel_relative_url:
                item['hotel_url'] = urljoin(response.url, hotel_relative_url)
            else:
                item['hotel_url'] = None

            yield item

        next_page_link = response.css('a[data-cy="pagination-next-button"]::attr(href)').get()
        if next_page_link:
            next_page_url = response.urljoin(next_page_link)
            self.logger.info(f"Following next page link: {next_page_url}")
            yield scrapy.Request(
                next_page_url,
                # meta={
                #     "playwright": True,
                #     "playwright_page_methods": [
                #         PageMethod("wait_for_selector", "div.PropertyCardItem"),
                #     ],
                # },
                callback=self.parse,
            )
            # yield CrawlbaseRequest(
            #     next_page_url,
            #     callback=self.parse,
            #     device='desktop',
            #     country='US',
            #     page_wait=1000,
            #     ajax_wait=True,
            #     dont_filter=True,
            # )
        else:
            self.logger.info(f"No next page link found on {response.url}. Finished scraping.")
            
    def parse(self, response):
        hotels = response.css('li[data-selenium="hotel-item"]')
        LOGGER.info(f"Found {len(hotels)} hotels on page: {response.url}")
        LOGGER.debug(f"Hotel data: {[hotel.get() for hotel in hotels]}")
        
        for hotel in hotels:
            item = ScraperItem()
            item['search_task_id'] = self.search_task_id
            item['source'] = self.name


            hotel_id = hotel.attrib.get('data-hotelid', '').strip()
            hotel_name = hotel.css('h3[data-selenium="hotel-name"]::text').get(default='').strip()
            
            # Hotel link
            relative_link = hotel.css('a.PropertyCard__Link::attr(href)').get()
            hotel_link = urljoin(response.url, relative_link) if relative_link else ''

            # Hotel image
            image_url = hotel.css('img.Imagestyled__ImageStyled-sc-zu5jhi-0::attr(src)').get(default='').strip()

            # Location
            location = hotel.css('span[data-selenium="area-city"]::text').get()
            if not location:
                # Fallback to aria-label or full text extraction
                location = hotel.xpath('.//div[@data-selenium="area-city"]/span/text()').get(default='').strip()

            # Star rating (count the icons)
            stars_count = len(hotel.css('[data-testid="rating-container"] svg'))

            # Rating & reviews
            rating_score = hotel.css('p[aria-hidden="true"] span::text').get(default='').strip()
            reviews = hotel.xpath('.//p[contains(text(), "reviews")]/text()').get(default='').strip()

            # Price info
            price_currency = hotel.css('div[data-element-name="price-before-cashback"] span.PropertyCardPrice__Currency::text').get(default='').strip()
            price_value = hotel.css('div[data-element-name="price-before-cashback"] span.PropertyCardPrice__Value::text').get(default='').strip()
            final_price = hotel.css('div[data-element-name="final-price"] span.PropertyCardPrice__Value::text').get(default='').strip()


            item['name'] = hotel_name
            item['location'] = location
            item['price'] = final_price
            item['rating'] = rating_score
            item['image_url'] = image_url
            item['hotel_url'] = hotel_link
            
            yield item

        # Pagination (if exists)
        next_page = response.css('a[data-selenium="pagination-next"]::attr(href)').get()
        if next_page:
            yield scrapy.Request(
                next_page,
                # meta={
                #     "playwright": True,
                #     "playwright_page_methods": [
                #         PageMethod("wait_for_selector", "div.PropertyCardItem"),
                #     ],
                # },
                callback=self.parse,
            )