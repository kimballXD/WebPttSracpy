# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy



class ArticleItem(scrapy.Item):
    aid = scrapy.Field()
    board = scrapy.Field()
    page = scrapy.Field()
    author = scrapy.Field()
    time = scrapy.Field()
    title = scrapy.Field()
    ip = scrapy.Field()
    country = scrapy.Field()
    country_flag = scrapy.Field()
    reply = scrapy.Field()    
    content = scrapy.Field()
    signature = scrapy.Field()
    category = scrapy.Field()
    comments = scrapy.Field()
    comment_users = scrapy.Field()
    score = scrapy.Field()    
    plus = scrapy.Field()
    minus = scrapy.Field()
    edit = scrapy.Field()
    comm_type = scrapy.Field()  # temp field
    comm_author = scrapy.Field() # temp field
    comm_content = scrapy.Field() # temp field
    comm_time = scrapy.Field() # temp field
        
class CommentItem(scrapy.Item):
    aid = scrapy.Field()    
    board = scrapy.Field()
    comm_author = scrapy.Field()
    comm_type = scrapy.Field()
    comm_time = scrapy.Field()
    comm_content = scrapy.Field()
    
