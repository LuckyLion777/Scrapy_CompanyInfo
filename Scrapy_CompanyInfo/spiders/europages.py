import scrapy
import math
import re
from Scrapy_CompanyInfo.items import EuropagesItem


class AlibabaCrawler(scrapy.Spider):
    name = 'europages_crawler'
    allowed_domains = ['www.europages.co.uk']
    start_urls = ['https://www.europages.co.uk/business-directory-europe.html']
    unique_data = set()

    def parse(self, response):
        cat_list = response.xpath('//div[@id="domain-columns"]//h2[@class="theme-title"]/a/@href').extract()
        for cat in cat_list:
            yield scrapy.Request(
                url=cat,
                callback=self.parse_sectors,
                dont_filter=True
            )

    def parse_sectors(self, response):
        href_list = response.xpath('//div[@id="domain-columns"]//li/a/@href').extract()
        sector_list = response.xpath('//div[@id="domain-columns"]//li/a/@title').extract()
        for i in range(len(href_list)):
            item = EuropagesItem()
            item['sector'] = sector_list[i]
            yield scrapy.Request(
                url=href_list[i],
                callback=self.parse_pages,
                meta={'item': item},
                dont_filter=True
            )

    def parse_pages(self, response):
        page_url = response.url.replace('companies/', 'companies/pg-{page_num}/')
        total_count = response.xpath('//div[@id="contentpage_blocktabs"]//span[@class="upper"]/text()').extract()
        if total_count:
            total_count = re.search('(\d+)', total_count[0], re.DOTALL)
            total_count = int(total_count.group(1)) if total_count else 0
        href_list = response.xpath('//div[contains(@class, "main-title")]/a[1]/@href').extract()

        for i in range(math.ceil(total_count / len(href_list))):
            yield scrapy.Request(
                url=page_url.format(page_num=str(i + 1)),
                callback=self.parse_company_links,
                meta=response.meta,
                dont_filter=True
            )

    def parse_company_links(self, response):
        item = response.meta.get('item')
        href_list = response.xpath('//div[contains(@class, "main-title")]/a[1]/@href').extract()
        company_name_list = response.xpath('//div[contains(@class, "main-title")]/a[1]/@title').extract()
        country_list = response.xpath('//span[@class="country-name"]/text()').extract()
        for i in range(len(href_list)):
            item['company_name'] = company_name_list[i]
            item['country'] = country_list[i]
            if href_list[i] and href_list[i] not in self.unique_data:
                self.unique_data.add(href_list[i])
                yield scrapy.Request(
                    url=href_list[i],
                    callback=self.parse_company,
                    meta=response.meta,
                    dont_filter=True
                )

    def parse_company(self, response):
        item = response.meta.get('item')

        website = response.xpath('//div[@class="website"]//span[@class="id-pagepeeker-data"]/@rel').extract()
        item['website'] = website[0] if website else None

        keywords = response.xpath('//ul[contains(@class, "keyList mt15")]/li/text()').extract()
        item['keywords'] = ', '.join(keywords)

        yield item