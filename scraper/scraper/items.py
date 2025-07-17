# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html


import scrapy

class ScraperItem(scrapy.Item):
    search_task_id = scrapy.Field()
    name = scrapy.Field()
    location = scrapy.Field()
    price = scrapy.Field()
    rating = scrapy.Field()
    image_url = scrapy.Field()
    hotel_url = scrapy.Field()
    source = scrapy.Field()
