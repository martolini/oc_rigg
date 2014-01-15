from scrapy.spider import BaseSpider
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from ocrigg.items import OcriggItem
import re

class OcSpider(BaseSpider):
	name = 'ocrigg'
	allowed_domains = ['pipelineme.com']
	start_urls = ['http://www.pipelineme.com/research/land-rigs/']

	def parse(self, response):
		hxs = HtmlXPathSelector(response)
		countries = [x for x in hxs.select('//select[@name="Country"]/option/@value').extract() if x]
		for country in countries:
			url = "http://www.pipelineme.com/research/land-rigs?Country=%s" % (country)
			yield Request(url=url, callback=self.yield_all_pages_from_country)

	def yield_all_pages_from_country(self, response):
		hxs = HtmlXPathSelector(response)
		last = -1
		try:
			last = int(hxs.select('//div[@class="pagination"]//a/@href').extract()[-2][-1])
		except:
			yield Request(url=response.url, callback=self.yield_riggs)
		if last >= 0:
			for page in range(1, last+1):
				url = "%s&page=%s" % (response.url, page)
				yield Request(url=url, callback=self.yield_riggs)

	def yield_riggs(self, response):
		hxs = HtmlXPathSelector(response)
		rigger = hxs.select('//ul[@class="news_pad"]//a/@href').extract()
		for rigg in rigger:
			url = "http://www.pipelineme.com%s" % (rigg)
			yield Request(url=url, callback=self.parse_rigg)

	def parse_rigg(self, response):
		hxs = HtmlXPathSelector(response)
		for elem in hxs.select('//p[@class="details_01"]'):
			item = OcriggItem()
			item['info'] = re.sub(r'\W+', '', elem.select('text()').extract()[0])
			item['description'] = elem.select('span/text()').extract()[0].strip()
			yield item
		


