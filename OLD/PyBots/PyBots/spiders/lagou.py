# -*- coding: utf-8 -*-
import datetime
import scrapy
import json
from PyBots.items import JobItem
from scrapy.selector import Selector
from scrapy.http import HtmlResponse
import re


class Tech2ipoSpider(scrapy.Spider):
    name = "lagou"
    allowed_domains = ["pro.lagou.com"]
    start_urls = [
        "https://pro.lagou.com/project/"
    ]


    def parse(self, response):
        # print('-----------------------')
        for sel in response.xpath('//div[@id="project_list"]/ul/li'):
            item = JobItem()
            item['platform'] = '大鲲网'
            item['title'] = sel.xpath('a/h3/text()').extract()[0].encode("utf-8")
            url = sel.xpath('a/@href').extract()[0]
            item['url'] = url
            item['checksum'] = '{}_{}'.format( 'pro_lagou', item['url'].split('/')[-1].split('.')[0] )
            item['price'] = sel.xpath('a/div[2]/span/text()').extract()[0].encode("utf-8").split('元')[0].split('-')[0]
            print item['url']
            # 查看次数
            # item['view_count'] = sel.xpath('a/div[4]/div[3]/div[2]/strong/text()').extract()[0].encode("utf-8")

            # expire_date 无
            categories = []
            for cats in sel.xpath('a/div[@class="category_list"]/span'):
                categories.append(cats.xpath('text()').extract()[0].encode("utf-8"))
            item['categories'] = categories
            item['roles'] = ''
            item['expire_date'] = ''
            request = scrapy.Request(url,callback=self.parse_contents)
            request.meta['item'] = item
            yield request

    def parse_contents(self, response):
        item = response.meta['item']
        item['skills'] = response.xpath('//div[@id="project_detail"]/div[1]/ul[1]/li[1]/span[2]/text()').extract()[0].split('/')
        # item['skills'] = response.xpath('//section[@class="skill-tags clearfix"]/dl/dd/text()').extract()
        body  = response.xpath('//div[@class="project_txt"]/pre/text()').extract()
        item['body'] = ''
        for c in body:
            item['body'] += c.encode("utf-8")
        release_date = response.xpath('//div[@id="project_detail"]/div[1]/ul[2]/li[1]/span[2]/text()').extract()[0].encode("utf-8")
        item['release_date'] = self.utc_rfc3339_string(release_date)
        return item

    def utc_rfc3339_string(self, str_date, format='%Y-%m-%d %H:%M:%S'):
        '''转化 datetime(UTC) 为 rfc3339 格式字符串'''
        dt = datetime.datetime.strptime(str_date, format)
        return dt.isoformat('T') + 'Z'
