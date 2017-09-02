# -*- coding: utf-8 -*-
# !/usr/bin/env python

import os
import sys
import time

import requests

from util.file_reader import parse_job_xml

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
#  gives you an absolute path for the parent directory of the directory your file is in

from spider.jobdetail_spider import crawl_job_detail
import pandas as pd
from util import log
from config.config import *

try:
    from urllib import parse as parse
except:
    import urllib as parse

    sys.reload()
    sys.setdefaultencoding('utf-8')  # what are these doing here?


def crawl_jobs(city, positionName):
    """crawl the job info from lagou H5 web pages"""
    JOB_DATA = list()
    max_page_number = get_max_pageNo(city, positionName)
    log.info("%s, 共有 %s 页记录, 共约 %s 记录", positionName, max_page_number, max_page_number * 15)
    cookies = get_cookies()

    for i in range(1, max_page_number + 1):
        request_url = 'https://m.lagou.com/search.json?city=' + parse.quote(city) + '&positionName=' + parse.quote(
            positionName) + '&pageNo=' + str(i) + '&pageSize=15'
        headers = {
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Host': 'm.lagou.com',
            'Referer': 'https://m.lagou.com/search.html',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/600.1.3 (KHTML, '
                          'like Gecko) Version/8.0 Mobile/12A4345d Safari/600.1.4',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive'
        }
        response = requests.get(request_url, headers=headers, cookies=cookies)
        if response.status_code == 200:
            for each_item in response.json()['content']['data']['page']['result']:
                JOB_DATA.append([each_item['positionId'], each_item['positionName'], each_item['city'],
                                 each_item['createTime'], each_item['salary'],
                                 each_item['companyId'], each_item['companyName'], each_item['companyFullName'], 'https://m.lagou.com/jobs/' + str(each_item['positionId']) + '.html'])
                # try:
                    # crawl_job_detail(each_item['positionId'], positionName)
                # except:
                #     pass
            print('crawling page %d done...' % i)
            time.sleep(TIME_SLEEP)
        elif response.status_code == 403:
            log.error('request is forbidden by the server...')
        else:
            log.error(response.status_code)

    return JOB_DATA


def get_cookies():
    """return the cookies after your first visit"""
    headers = {
        'Host': 'm.lagou.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/600.1.3 (KHTML, like Gecko) Version/8.0 Mobile/12A4345d Safari/600.1.4'
    }
    url = 'https://m.lagou.com/'
    response = requests.get(url, headers=headers, timeout=10)

    return response.cookies


def get_max_pageNo(city, positionName):
    """return the max page number of a specific job"""
    cookies = get_cookies()
    request_url = 'https://m.lagou.com/search.json?city=' + parse.quote(city) + '&positionName=' + parse.quote(
            positionName) + '&pageNo=1&pageSize=15'
    headers = {
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Host': 'm.lagou.com',
        'Referer': 'https://m.lagou.com/search.html',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/600.1.3 (KHTML, like Gecko) '
                      'Version/8.0 Mobile/12A4345d Safari/600.1.4',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive'
    }
    response = requests.get(request_url, headers=headers, cookies=cookies, timeout=10)
    print("Getting data from %s successfully~" % positionName + request_url)
    if response.status_code == 200:
        max_page_no = int(int(response.json()['content']['data']['page']['totalCount']) / 15 + 1)

        return max_page_no
    elif response.status_code == 403:
        log.error('request is forbidden by the server...')

        return 0
    else:
        log.error(response.status_code)

        return 0


if __name__ == '__main__':
    craw_job_list = parse_job_xml('../config/job.xml')
    city = input('城市名称>>')
    for _ in craw_job_list:
        joblist = crawl_jobs(city, _)
        col = [
            u'职位编码',
            u'职位名称',
            u'所在城市',
            u'发布日期',
            u'薪资待遇',
            u'公司编码',
            u'公司名称',
            u'公司全称',
            u'职位链接']
        df = pd.DataFrame(joblist, columns=col)
        path = "/Users/shellva/Desktop/LagouJob/data/"
        df.to_excel(path + _ + ".xlsx", sheet_name=_, index=False)
