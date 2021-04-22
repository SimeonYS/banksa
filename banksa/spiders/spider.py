import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import BbanksaItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class BbanksaSpider(scrapy.Spider):
	name = 'banksa'
	start_urls = ['https://www.banksa.com.au/about/media/archive']
	flag = 0
	def parse(self, response):
		articles = response.xpath('//p[@class=" top-margin2-xs"]//a')
		term = 1

		for index in range(len(articles)):
			link = response.xpath(f'(//p[@class=" top-margin2-xs"]//a)[{index + 1}]/@href').get()
			date = response.xpath(f'(//p[@class=" top-margin2-xs"])[position()=2+({term}-1)*3]//text()').get()
			date = re.findall(r'\d+\s\w+\s\d+', date)

			term += 1
			yield response.follow(link, self.parse_post, cb_kwargs=dict(date=date))

	def parse_post(self, response, date):
		title = response.xpath('//div[@class="lead top-margin3-xs"]/p//text()').get()
		if not title:
			title = response.xpath('//div[@class="lead top-margin3-xs"]/text()').get()
		content = response.xpath('//div[@class="body-copy4 parbase section"]//text()[not (ancestor::script)]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=BbanksaItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
