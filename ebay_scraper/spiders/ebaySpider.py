# -*- coding: utf-8 -*-
import scrapy
import logging



class EbaySpider(scrapy.Spider):
	name = 'ebaySpider'
	allowed_domains = ['ebay.com']
	start_urls = ['https://www.ebay.com/str/tinkinwanhua?_pgn=1']

	def __init__(self):
		self.num_of_pages = int(input("How many pages to scrape?\n"))
		
		self.all_categories = []
		self.tags = open("tags.txt", "r").readline().split(",")
		self.tags = [i.strip() for i in self.tags]
		self.stopwords = ['Read more',
		                  'about the condition',
		                  'See all condition definitions',
		                  '- opens in a new window or tab',
		                  '...']

	def parse(self, response):
		num_of_pages = self.num_of_pages
		if num_of_pages == 1:
			links = response.xpath("//a[contains(@class, 's-item__link')]/@href").getall()
			for i in links:
				yield scrapy.Request(i, self.parse_item)
		else:
			for page in range(2, num_of_pages + 1):
				links = response.xpath("//a[contains(@class, 's-item__link')]/@href").getall()
				for i in links:
					yield scrapy.Request(i, self.parse_item)
				full_url = 'https://www.ebay.com/str/tinkinwanhua?_pgn=' + str(page)
				yield scrapy.Request(full_url, self.parse)

	def parse_item(self, response):
		url = response.url
		name = response.xpath("//h1[@id='itemTitle']/text()").get()
		cond = response.xpath("//div[@id='vi-itm-cond']/text()").get()
		price = response.xpath("//*[@itemprop='price']/text()").get()
		image_url = response.xpath("//img[@id='icImg']/@src").get()
		attrs = response.xpath(
			"//td[contains(@class, 'attrLabels')]/text() | //td[@width='50.0%']/span/text() | //td/h2//text() "
			"| //div[@aria-live = 'polite']//text()").getall()
		clean_attrs = [i.strip() for i in attrs if i.strip() != '' and i.strip() not in self.stopwords]
		if response.xpath("//span[@id='readFull']"):
			clean_attrs.pop(0)
			second = ""
			count = 0
			for i in clean_attrs:
				if i not in self.tags:
					second += i
					count += 1
				else:
					break
			clean_attrs = clean_attrs[count:]
			keys = ["FullCondition:"] + [clean_attrs[i] for i in range(0, len(clean_attrs), 2)]
			values = [second] + [clean_attrs[i] for i in range(1, len(clean_attrs), 2)]
			specifics = dict(zip(keys, values))
		else:
			keys = [clean_attrs[i] for i in range(0, len(clean_attrs), 2)]
			values = [clean_attrs[i] for i in range(1, len(clean_attrs), 2)]
			specifics = dict(zip(keys, values))
		yield {'name': name, 'cond': cond, 'price': price, **specifics, 'image': image_url, 'url': url}
