# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CsdnScraperItem(scrapy.Item):
    article_url = scrapy.Field()
    article_title = scrapy.Field()
    article_content = scrapy.Field()
    search_data = scrapy.Field()

