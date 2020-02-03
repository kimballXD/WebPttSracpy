# Yet Another Scrapy-Based Web PTT Crawler

A crawler scarps posts and comments from [Web PTT](https://www.ptt.cc/bbs/index.html) bulletin board system.

The crawler is built upon Python crawler framework *scrapy*. To know what are the options you have when you want to change the default behavior of the crawler, check the [settings documentation](https://docs.scrapy.org/en/latest/topics/settings.html) of the *scrapy*.

### Feature

- Robust: correctly parse the post content, time of the post, and the IP address of poster even if user scramble the post content with ad-hoc editing.
- Flexible: carefully designed command line arguments let you fetch posts in flexible way. 

### Environment

- python 3.6, with the following 3rd-party packages:
  - `scrapy`
  - `BeautifulSoup4`
  - `Pandas`
  - [`geoip2`](https://pypi.org/project/geoip2/) for geolocation parsing of IP address

###  Usage

The crawler needs to be executed in command line with correct set of arguments.  The following sections explain the common use cases and the corresponding argument sets.

---------------------



#### Normal case: crawl posts of a discussion board during specific date range 

##### command format
`scrapy crawl ptt -a board=BOARD -a start=START -a end=END`

##### example

`scrapy crawl ptt -a board=Gossiping -a start=2019-11-06 -a end=2019-11-07`

This command will fetch all of the posts and comments posted in [Gossiping](https://www.ptt.cc/bbs/Gossiping/index.html) discussion board from Nov 6th, 2019 to Nov 7th, 2019

##### arguments

- board: name of the discussion board to be crawled. Case sensitive.
- start: the earliest date of the crawled posts. Specified with YYYY-MM-DD format. 
- end: the latest date of the crawled post. Specified with YYYY-MM-DD date format. 

##### output

- `./data/articles.csv`: post content and metadata of the posts
- `./data/comments.csv`: comments under the posts

------



#### Test case: crawl posts of a discussion board showed on specific page(s) 

##### command format

`scrapy crawl ptt -a board=BOARD -a page=PAGE [-a testpages=TESTPAGES]`

##### example

`scrapy crawl ptt -a board=Gossiping -a page=39224`

This example command crawls all of the posts show on the index page https://www.ptt.cc/bbs/Gossiping/index39224.html of Gossiping discussion board.

`scrapy crawl ptt -a board=Gossiping -a page=39224 -a testpages=2`

This example command crawls all of the posts show on the **two** index pages of Gossiping discussion board, starting from index page 39224 in decreasing order. In other word, it crawls index page 39224 and 39223 of Gossiping discussion board.

##### arguments

- board: name of the discussion board to be crawled. Case sensitive.
- page: the page index where the crawling begins. 
- testpages: the number of pages that crawler will crawl. Optional, default 1.

##### output

- `./data/articles.csv`: post content and metadata of the posts
- `./data/comments.csv`: comments under the posts

------------------



#### Test case:  crawl one specific post

##### command format

`scrapy crawl ptt -a board=BOARD -a page=PAGE -a aid=AID`

##### example

`scrapy crawl ptt -a board=Gossiping -a page=39224 -a aid=M.1573149639.A.355`

This example command will fetch the post which the article ID is M.1573149639.A.355 and is posted in the index page 39224 of Gossiping discussion board.

##### arguments

- board: name of the discussion board to be crawled. Case sensitive.
- page: the page index where the crawling begins. 
- aid: article ID. You can find them in the URL of the post.

##### output

- `./data/articles.csv`: post content and metadata of the posts
- `./data/comments.csv`: comments under the posts

