import scrapy
from Scrapy_CompanyInfo.items import CompanyProductItem
from urllib.parse import urljoin


class GreekexportersCrawler(scrapy.Spider):
    name = 'greekexporters_crawler'
    allowed_domains = ['www.greekexporters.gr']
    start_urls = ['http://www.greekexporters.gr/']
    unique_data = set()

    def parse(self, response):
        cat_list = response.xpath('//div[@id="categories"]//a/@href').extract()
        for cat in cat_list:
            yield scrapy.Request(
                url=urljoin(response.url, cat),
                callback=self.parse_pages,
                dont_filter=True
            )

    def parse_pages(self, response):
        page_count = response.xpath('//div[@class="pagin"]/a[last()-1]/text()').extract_first()
        if not page_count:
            page_count = 1
        for i in range(int(page_count)):
            yield scrapy.Request(
                url=response.url + '/' + str(i+1),
                callback=self.parse_links
            )

    def parse_links(self, response):
        link_list = response.xpath('//h3[@class="resTitle"]/a/@href').extract()
        for link in link_list:
            yield scrapy.Request(
                url='http://www.greekexporters.gr/' + link,
                callback=self.parse_company
            )

    def parse_company(self, response):
        item = CompanyProductItem()
        item['company_name'] = response.xpath('//div[@id="address"]/h2/text()').extract_first()
        item['country'] = response.xpath('//div[@id="address"]/p/text()[last()-1]').extract_first().strip()
        item['website'] = response.xpath('//div[@id="contact"]/div[@class="imgs"][1]/a/text()').extract_first()
        if item['website'] == 'http://':
            item['website'] = None
        item['telephone'] = response.xpath('//div[text()="telephone:"]/following-sibling::div[1]//text()').extract()
        item['email'] = response.xpath('//div[@id="address"]/h2/text()').extract_first()
        item['products'] = response.xpath('//div[text()="PRODUCTS / SERVICES"]/following-sibling::div[1]/text()').extract_first().strip()
        item['skype'] = response.xpath('//div[text()="skype id:"]/following-sibling::div[1]/text()').extract_first()

        item['link'] = response.url
        yield item
