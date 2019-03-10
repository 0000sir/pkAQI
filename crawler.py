#! /usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from urlparse import urljoin
import codecs
from bs4 import BeautifulSoup
import sys
import os
import argparse
import time, threading
from influxdb import InfluxDBClient
from pprint import pprint
import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

MONTH_URL = "https://www.aqistudy.cn/historydata/monthdata.php?city="
INFLUXDB = InfluxDBClient('localhost', 8086, 'root', 'root', 'air_quality')

chrome_options = Options()
chrome_options.add_argument("--headless")
browser = webdriver.Chrome(executable_path=(r'/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome'), chrome_options=chrome_options)

def read_month_page(url):
    html = requests.get(url).content
    soup = BeautifulSoup(html, features="html5lib")
    month_list = soup.find('ul', attrs={'class': 'unstyled1'})
    urls = []
    for daily_url in month_list.find_all('a'):
        raw_url = daily_url.get('href')
        month = daily_url.getText()
        month = month.replace(u"年", "-")
        month = month.replace(u"月", "")
        urls.append({'month': month, 'url': raw_url})
    return urls

def read_daily_page(url):
    url = "https://www.aqistudy.cn/historydata/" + url
    print(url)
    html = browser.get(url)
    pprint(html)


def write_city_urls(city, urls):
    with open(city+'.json', 'w') as outfile:
        json.dump(urls, outfile)

def read_city_urls(city):
    with open(city+'.json') as json_data:
        return json.load(json_data)


city = "杭州"
#write_city_urls(city, read_month_page(MONTH_URL + city))

daily_urls = read_city_urls(city)
read_daily_page(daily_urls[0]['url'])