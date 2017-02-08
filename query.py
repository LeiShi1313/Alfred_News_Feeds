#!/usr/bin/python
# encoding: utf-8
import sys
from workflow import Workflow3, ICON_WEB
import json
import datetime
import time
import requests
from bs4 import BeautifulSoup as bs
from eventregistry import *

def get_news(today='1997-01-01', count=30):
    if today=='1997-01-01':
        today=datetime.datetime.now().strftime('%Y-%m-%d')
    er = EventRegistry(apiKey='866f6705-7aa4-4fa7-9ba0-4956283e7df9')
    q = GetTopSharedArticles(date=today, count=count)
    return er.execQuery(q)

def get_verge():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'
        }
    req = requests.get('http://www.theverge.com/rss/index.xml', headers=headers)
    soup = bs(req.text, 'lxml')
    return soup

def main(wf):
    # Save data from `get_web_data` for 30 seconds under
    # the key ``example``
    if len(wf.args):
        query = wf.args
        method = wf.args[0]
        keyword = wf.args[1:]
    else:
        query = None
    if method == 'er':
        today=datetime.datetime.now().strftime('%Y-%m-%d')
        articles = wf.cached_data("articles", get_news, max_age=600)
        for i,article in enumerate(articles[today]):
            # wf.logger.info(article['lang'])
            if article['lang'] == 'eng' or article['lang'] == 'zho':
                wf.add_item(
                    article['title'],
                    subtitle=article['url'],
                    largetext=article['title'] + '\n' + article['body'],
                    arg=article['url'],
                    quicklookurl=article['title'],
                    valid=True)
    elif method == 'verge':
        verge_soup = wf.cached_data("verge_soup", get_verge, max_age=600)
        for entry in verge_soup.find_all('entry'):
            s = bs(entry.content.text, 'html.parser')
            wf.add_item(
                entry.title.text,
                subtitle=s.p.text,
                arg=entry.link.get('href'),
                largetext = entry.title.text + '\n' + s.p.text,
                valid=True)
    else:
        wf.add_item("There is nothing to fetch...")

    wf.send_feedback()

if __name__ == '__main__':
    wf = Workflow3()
    sys.exit(wf.run(main))
