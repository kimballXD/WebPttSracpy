# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import re
from datetime import datetime
import pickle
import pandas as pd
from scrapy.exporters import CsvItemExporter
import geoip2
import geoip2.database as geoipdb
from ptt.items import CommentItem

# debugging
#os.chdir('C:\\Coding\\scrapy_projects\\ptt\\ptt')
#a = pd.read_csv('test.csv')
#item= a.iloc[20,]

#%%

class ArticlePipeline(object):    
    def __init__(self):
        # set up comment file output
        self.comment_file = open("./data/comments.csv",'wb')
        self.comment_exporter = CsvItemExporter(self.comment_file)
        self.comment_exporter.start_exporting()
        
        # set up article output fields heeeeeeere!
        self.article_file = open("./data/article.csv",'wb')        
        field_to_export = ['aid','board','page','author',
                           'reply','category','title','time','ip','country','country_flag',
                           'content','signature',
                           'comments','comment_users','score','plus','minus','edit']
        self.article_exporter = CsvItemExporter(self.article_file,
                                                fields_to_export = field_to_export)
        self.article_exporter.start_exporting()
    
        # ip-country check
        self.country_dbcon = geoipdb.Reader('./db/GeoLite2-Country.mmdb')        
        with open('./db/country_dict.pckl','rb') as infile:
            self.country_dict = pickle.load(infile)
                    
    def close_spider(self, spider):
        self.comment_exporter.finish_exporting()
        self.comment_file.close()        
        self.article_exporter.finish_exporting()
        self.article_file.close()
        self.country_dbcon.close()    

#%% item parse

    def _check_country(self, item):
        flag = 0
        if item['country'] is None or item['country'] not in self.country_dict.values():
            flag = 1
            try:
                lookup = self.country_dbcon.country(item['ip'])
                country = self.country_dict.get(lookup.country.iso_code, 'country_na')
                return country, flag
            except geoip2.errors.AddressNotFoundError:
                return 'ip_na', flag
            except ValueError:
                return 'ip_wrong', flag
        else:
            return item['country'], flag
        
    def process_item(self, item, spider):        
        # clean article data
        item['time'] = datetime.strptime(item['time'], '%a %b  %d %H:%M:%S %Y')
        item['country'] = re.sub('[\(\)]','', item['country']) if item['country'] else None
        country, country_flag = self._check_country(item)
        item['country'] = country
        item['country_flag'] = country_flag
        title_re = re.search('(Re: )?(\[.+?\])?(.+)', item['title'])
        item['reply'] = 1 if title_re.group(1) else 0
        item['category'] = re.sub('[\[\]]','', title_re.group(2)) if title_re.group(2) else None        
        item['title'] = title_re.group(3).strip()
        item['content'] = item['content'].strip() if item['content'] else None
        item['signature'] = re.sub('^[\-\n]+','', item['signature']) if item['signature'] else None
        
        # clean comment data and dump
        data = zip(item['comm_author'], item['comm_time'], item['comm_type'], item['comm_content'])
        comms = pd.DataFrame(data, columns=['comm_author','comm_time','comm_type','comm_content'])
        def time_translate(x):
            try:
                return datetime.strptime('{}/{}'.format(item['time'].year, x.strip()),'%Y/%m/%d %H:%M')
            except ValueError:
                return None
        comms['comm_time'] = comms['comm_time'].apply(time_translate)
        comms['comm_type'] = comms['comm_type'].str.strip().replace({u'→':0,u'推':1,u'噓':-1})        
        comms['comm_content'] = comms['comm_content'].replace('^:?','',regex=True).str.strip()
                
        for idx, row in comms.iterrows():
            commItem = CommentItem()
            commItem['aid'] = item['aid']
            commItem['board'] = item['board']
            commItem['comm_author'] = row['comm_author']
            commItem['comm_time'] = row['comm_time']
            commItem['comm_type'] = row['comm_type']
            commItem['comm_content'] = row['comm_content']
            self.comment_exporter.export_item(commItem)

        # calculate comment columns for article 
        item['comments'] = len(comms)
        item['comment_users'] = len(comms.comm_author.unique())
        if item['comments']:           
            score_stat = comms.comm_type.value_counts()
            item['plus'] = score_stat[1] if 1 in score_stat.index else 0
            item['minus'] = score_stat[-1] if -1 in score_stat.index else 0
            item['score'] = item['plus']- item['minus']
        else:
            item['plus'] = 0
            item['minus'] = 0
            item['score'] = 0
            
        # dump article data               
        self.article_exporter.export_item(item)        
        return item
