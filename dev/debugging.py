# -*- coding: utf-8 -*-
"""
Created on Tue Jun  4 09:05:12 2019

@author: Wu
"""
import os
import crawlerUtil as crawlUtil
import re
import subprocess
import pandas as pd



#%% simply check result

os.chdir('C:\\Coding\\scrapy_projects\\ptt')
article = pd.read_csv('data/article.csv')
comm = pd.read_csv('data/comments.csv')


#%%

article = pd.read_csv('data/article_mdl.csv', nrows=0)
comm = pd.read_csv('data/comments_mdl.csv', nrows=0)
log_file = 'fail_log.txt'
if os.path.isfile(log_file):
    os.remove(log_file)
cmd_format = 'scrapy crawl ptt --logfile={} -a board=Gossiping -a days=0 -a debug_index="{}" -a debug_url="{}"'

with open('failed.txt','r') as f:
    urls = [x.strip().split() for x in f.readlines()]

urls_len = len(urls)
fail_count = 0
for idx, url in enumerate(urls):
    print('Check url {}/{}.....'.format(idx+1, urls_len))
    cmd = cmd_format.format(log_file, *url)
    subprocess.call(cmd, shell=True)
    with open('fail_log.txt') as fl:
        tmp_failed_count = len(re.findall('\[scrapy\.core\.scraper\] ERROR',fl.read()))
        
        if tmp_failed_count==fail_count +1:
            fail_count +=1
            print('CHECK FAILED: {} {}'.format(*url))
            continue
    try:        
        tmp_article = pd.read_csv('data/article.csv')
        tmp_comm = pd.read_csv('data/comments.csv')
    except pd.errors.EmptyDataError:
        print('Empty Data! {}/{}.....'.format(idx+1, urls_len))
        
    article = article.append(tmp_article)
    comm = comm.append(tmp_comm)

#%%

