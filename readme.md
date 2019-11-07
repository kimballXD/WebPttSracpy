# Yet Another Scrapy-Based Web PTT Crawler

A crawler crawls posts and comments from [Web PTT](https://www.ptt.cc/bbs/index.html) bulletin board system.

The crawler is built with a Python crawler framework *scrapy*. To know what are the options you have when you want to change the default behavior of the crawler, check the [settings documentation](https://docs.scrapy.org/en/latest/topics/settings.html) of the *scrapy*.

### Feature

- Robust: correctly parse the content, post time, and IP even if user scramble the post format with ad-hoc editing.
- Flexible: carefully designed command line arguments let you fetch posts in flexible way. 

### Environment

- python 3.6
- 3rd-party packages:
  - `scrapy`
  - `BeautifulSoup 4`
  - `Pandas`
  - `geoip2` for geolocation parsing of IP address

###  Usage

The crawler need to be executed in command line with the correct set of arguments.  The following explains the common use cases of the command line execution. 

#### Normal case: crawl posts of a discussion board in specific date range 

`scrapy crawl ptt -a board={board name} -a start={start date} -a end={end Date} `

Example: scrapy crawl ptt -a board=Gossiping  -a start=2019-11-06 -a end=2019-11-07

The example will fetch all of the posts posted in [Gossiping](https://www.ptt.cc/bbs/Gossiping/index.html) discussion board during Nov 7th, 2019 and respective post comments. 

- Arguments:
  - board name: name of the discussion board as it shows in the URL. **Case sensitive**.
  - start date, end date: YYYY-MM-DD date format. 
- Output
  - `./data/articles.csv`: content and metadata of the posts
  - `./data/comments.csv`: comments under the posts

### 

#### Test case:  crawl posts of a discussion board show on specific index page(s)

`scrapy crawl ptt -a board={board name} -a page={page index} -a testpages={# of pages}`

Example: scrapy crawl ptt -a board=Gossping -a page=39224

The example crawls all of the posts show on the index page https://www.ptt.cc/bbs/Gossiping/index39224.html of Gossiping discussion board.  

Example: scrapy crawl ptt -a board=Gossping -a page=39224 -a testpages=2

The example crawls all of the posts show on the **two** index pages of Gossiping discussion board, starting from index page 39224 in decreasing order. In other word, it crawls index page 39224 and 39223.

- Arguments
  - page: the index page which crawler starts to crawl
  - testpages: number of pages that crawler will crawl. **Optional, default 1.**

For the definition of the rest of arguments and the outputs, please sees the normal case.



#### Test case:  crawl one specific post using article ID

```
scrapy crawl ptt -a board={board name} -a page={page index} -a aid={article ID}
```

Example: scrapy crawl ptt -a board=Gossiping -a page=39224 -a aid=M.1573149639.A.355

The example will crawl the post which has the article ID as M.1573149639.A.355 posted in the index page 39224 of Gossiping discussion board

- Arguments
  - page: the index page which crawler starts to crawl
  - testpages: number of pages that crawler will crawl. **Optional, default 1.**

For the definition of the rest of arguments and the outputs, please sees the normal case.

