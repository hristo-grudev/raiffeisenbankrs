import json

import scrapy

from scrapy.loader import ItemLoader
from w3lib.html import remove_tags

from ..items import RaiffeisenbankrsItem
from itemloaders.processors import TakeFirst

import requests

url = "https://www.raiffeisenbank.rs/wp-content/uploads/news/news.json"

payload = {}
headers = {
  'Connection': 'keep-alive',
  'Pragma': 'no-cache',
  'Cache-Control': 'no-cache',
  'sec-ch-ua': '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
  'Accept': 'application/json, text/plain, */*',
  'sec-ch-ua-mobile': '?0',
  'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36',
  'Sec-Fetch-Site': 'same-origin',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Dest': 'empty',
  'Referer': 'https://www.raiffeisenbank.rs/vesti/',
  'Accept-Language': 'en-US,en;q=0.9,bg;q=0.8',
  'Cookie': '_gcl_au=1.1.9381442.1614688765; _ga=GA1.2.181573572.1614688765; _fbp=fb.1.1614688765021.620683288; _hjid=1afab8df-a0cf-48bb-913c-fe3590cfa7cd; _hjTLDTest=1; _gid=GA1.2.488961744.1614945675; _gat_gtag_UA_2100374_1=1; _gat_UA-170298402-5=1; _hjIncludedInSessionSample=0; _hjAbsoluteSessionInProgress=0; _pk_ses.1.679a=1; _pk_id.1.679a=15ea3eb003cb4d44.1614688765.2.1614945708.1614945675.'
}


class RaiffeisenbankrsSpider(scrapy.Spider):
	name = 'raiffeisenbankrs'
	start_urls = ['https://www.raiffeisenbank.rs/vesti/']

	def parse(self, response):
		raw_data = requests.request("GET", url, headers=headers, data=payload)
		data = json.loads(raw_data.text)
		for post in data:
			link = post["permalink"]
			title = post["title"]
			date = post["publish_time"]
			yield response.follow(link, self.parse_post, cb_kwargs={'date': date, 'title': title})

	def parse_post(self, response, date, title):
		description = response.xpath('//div[@class="article-section"]//text()[normalize-space()]').getall()
		description = [remove_tags(p).strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=RaiffeisenbankrsItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
