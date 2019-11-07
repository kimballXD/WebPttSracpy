# -*- coding: utf-8 -*-
"""
Created on Mon Feb  4 16:47:11 2019

@author: Wu
"""
import datetime
import re
import scrapy
from ptt.items import ArticleItem
from bs4 import BeautifulSoup as bs

#%%
   
class PTTSpider(scrapy.Spider):
    name='ptt'    
    def start_requests(self):
        url_format ='https://www.ptt.cc/bbs/{}/index{}.html'
        page = getattr(self,'page',0)
        
        urls = [url_format.format(self.board, page)]
        for url in urls:
            yield scrapy.Request(url = url,
                                 cookies = {'over18':'1'},
                                 callback = self.parse)

#%% article parse

    def _post_date_parse(self):
        if 'date_parse' in self.__dict__:
            return self.date_parse
        else:            
            post_date = self.response.meta.get('post_date')
            date_parse = post_date.strftime('%a %b %d %Y').split()
            date_parse[2] = int(date_parse[2])
            self.date_parse = date_parse
            return self.date_parse

    def _edit_search(self, soup, author):
        if 'edit' in self.__dict__:
            return self.edit
        else:
            self.edit={}                        
            ZH=u'\u4E00-\u9FA5\uF900-\uFAFF'
            ip_pattern = u'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}' 
            date_pattern = u'(1[0-2]|0[1-9])/(0[1-9]|[12][0-9]|3[01])/20\d\d'
            time_pattern = u'(2[0-3]|[01][0-9]):[0-5][0-9]:[0-5][0-9]'
            edit_pattern = u'※ 編輯: {author} \(({ip})([ {country}]+)?\), {date} {time}'
            edit_pattern = edit_pattern.format(author = author,
                                               ip=ip_pattern,
                                               country = ZH,
                                               date = date_pattern,
                                               time = time_pattern)
            edit = re.search(edit_pattern, soup.text)
            
            # output
            date_parse = self._post_date_parse()
            time = edit.group(0).split()[-1]
            time = '{0} {1}  {2} {4} {3}'.format(*date_parse, time)
            self.edit['ip'] = edit.group(1)
            self.edit['country'] = edit.group(2)
            self.edit['time'] = time
            return self.edit
        
    def parse_article(self, response):        
        """
        TODO:
            use info in index page
            try catch on columns that easy to be modify
        """
        edit_flag = 0
        article = ArticleItem()
        article['aid'] = response.url.split('/')[-1].replace('.html','')
        article['board'] = self.board
        article['page'] = response.meta.get('page')

        # preparing 
        soup = bs(response.text, 'lxml')
        self.response = response
        
        # header
        index_item = response.meta.get('index_item')
        article['author'] = index_item.css('.author::text').get()
        article['title'] = index_item.css('.title a::text').get()    
        article_value = soup.select('.article-meta-value')
        if article_value and len(article_value)==4:            
            article['time'] = article_value[3].text
        else:
            # edit header
            edit_flag = edit_flag + 1
            date_parse = self._post_date_parse()
            date_pattern = '時間({} {}\s+{} (2[0-3]|[01][0-9]):[0-5][0-9]:[0-5][0-9] {})'.format(*date_parse)
            post_time = re.search(date_pattern.format(*date_parse), soup.text)
            if post_time:
                article['time'] = post_time.group(1)
            else:
                # edit time in header
                edit_flag = edit_flag + 2
                edit = self._edit_search(soup, article['author'])
                article['time'] = edit['time']
                            
        # footer
        ZH=u'\u4E00-\u9FA5\uF900-\uFAFF'
        ip_pattern = u'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}' 
        source_pattern =u'來自: ({})[\s]*(\([{}]*\))?'.format(ip_pattern, ZH) # two groups
        url_pattern =u'※ 文章網址:(.+?)\.html' # the third group 
        footer_pattern =u'※ 發信站: 批踢踢實業坊\(ptt\.cc\), {}\s+{}'.format(source_pattern, url_pattern)
        footer_re =re.compile(footer_pattern, flags=re.DOTALL)
        footer = re.search(footer_re, soup.text)
        if footer:
            article['ip'] = footer.group(1)
            article['country'] = footer.group(2)
        else: 
            # edit footer
            edit_flag = edit_flag + 4
            edit = self._edit_search(soup, article['author'])
            article['ip'] = edit['ip']
            article['country'] = edit['country']

        # content 
        content_re =u'時間{}(.+?)?([\-]+\n.+?)?\-\-\n(※ 文章網址|※ 發信站:)'.format(article['time'])
        content = re.search(content_re, soup.text, flags=re.DOTALL)
        article['content'] = content.group(1) if content else None
        article['signature'] = content.group(2) if content else None
        
        # comments
        article['comm_type'] = [x.text for x in soup.select('.push-tag')]
        article['comm_author'] = [x.text for x in soup.select('.push-userid')]
        article['comm_content'] = [x.text for x in soup.select('.push-content')] # do we need graph informtaion (if any) in comments?
        article['comm_time'] = [x.text for x in soup.select('.push-ipdatetime')]                
        
        # edit behavoir
        article['edit'] = edit_flag
        yield article

#%% index page parse

    def _get_testrun_info(self):
        if not hasattr(self, 'date_info'):            
            testrun = hasattr(self, 'page')
            testpages = int(getattr(self, 'testpages', 1)) 
            aid = getattr(self, 'aid', None)
            testurl = '/bbs/{}/{}.html'.format(self.board, aid) if aid else None            
            self.testrun_info = [testrun, testpages, testurl]
        return self.testrun_info
        
    def _get_date_info(self, testrun):
        if not hasattr(self, 'date_info'):
            start =  getattr(self, 'start', None)
            start = datetime.date.today() if not start else datetime.date.fromisoformat(start)                    
            end = None
            if not testrun:
                end =  getattr(self, 'end', None)
                if end:
                    end = datetime.date.fromisoformat(end)
                else:
                    days = getattr(self, 'days', None)
                    if not days:
                        raise ValueError('[ERROR] Missing Commandline Argument: Must specify either ${end} or ${days}.')
                    end = start - datetime.timedelta(days= int(days))            
            self.date_info = [start, end]        
        return self.date_info
    
    def _get_item_list(self, response):
        if not hasattr(self, 'index_page_flag'):
            items = response.css('.r-list-container>div')[1:] # drop search bar
            for idx, item in enumerate(items):
                if item.css('.r-list-sep'):
                    items = items[:idx]
                    break
            self.index_page_flag=True
        else:
            items = response.css('.r-ent')
            
        items.reverse()
        return items
    
    def parse(self, response):
        """
        """
        # get job info
        testrun, testpages, testurl = self._get_testrun_info()
        start, end = self._get_date_info(testrun)
        
        # get item list 
        items = self._get_item_list(response)
        # crawl this index page 
        close_flag = False
        for idx, item in enumerate(items):            
            # which day does the post posted??            
            post_date = item.css('.date::text').get().split('/')
            post_year = start.year if not getattr(self, 'crossyear', None) else start.year+1
            post_date = [post_year] + [int(i) for i in post_date]
            post_date = datetime.date(*post_date)

            # meta
            meta= {'page':re.search('/index(\d+)?\.html',response.url).groups('')[0],
                   'index_item':item,
                   'post_date':post_date}
            
            # processing 
            if testrun:
                # testrun
                href = item.css('.title a::attr(href)').get()
                need_crawl = (testrun and testurl==href) or not testurl
                if href and need_crawl:                    
                    yield response.follow(href, self.parse_article, meta=meta)
                continue         
            else:
                # normal process
                if post_date > start:
                    continue
                elif post_date <= start and post_date >= end:                
                    href = item.css('.title a::attr(href)').get()
                    if href:
                        yield response.follow(href, self.parse_article, meta=meta)
                elif post_date < end:
                    close_flag = True
                    break
                
        # assign close_flag for testrun
        if testrun:
            self.testrun_info[1] = testpages - 1 
            self.logger.info('testpages:{}'.format(self.testrun_info[1]))
            close_flag = True if self.testrun_info[1] == 0 else False

        # proceed to next index page?
        if not close_flag:
            next_page = response.css('.btn-group-paging > a::attr(href)').getall()[1]
            yield response.follow(next_page, self.parse)

