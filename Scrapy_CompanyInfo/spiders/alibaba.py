import scrapy
import math
import re
from Scrapy_CompanyInfo.items import CompanyItem
from urllib.parse import urljoin


class AlibabaCrawler(scrapy.Spider):
    name = 'alibaba_crawler'
    allowed_domains = ['alibaba.com']
    start_urls = ['https://www.alibaba.com/companies']

    def parse(self, response):
        cat_list = response.xpath('//div[contains(@class, "g-cate")]/dl/dt/a/@href').extract()
        for cat in cat_list:
            yield scrapy.Request(
                url=cat,
                callback=self.parse_category
            )

    def parse_category(self, response):
        cat_list = response.xpath('//div[@id="category-main-box"]/div/ul/li/a/@href').extract()
        for cat in cat_list:
            yield scrapy.Request(
                url=urljoin(response.url, cat),
                callback=self.parse_pagination
            )

    def parse_pagination(self, response):
        count = response.xpath('//div[contains(@class, "ui-breadcrumb")]/span[contains(text(), "Supplier")]'
                               '/preceding-sibling::span[1]/text()').extract()
        count = int(count[0].replace(',', '')) if count else 0

        pagination_link = response.xpath('//div[contains(@class, "ui2-pagination-pages")]/a[1]/@href').extract()
        pagination_link = pagination_link[0][:-1] if pagination_link else None
        for i in range(math.ceil((count-10)/38)):
            yield scrapy.Request(
                url=pagination_link + str(i+1),
                callback=self.parse_page
            )

    def parse_page(self, response):
        href_list = response.xpath('//div[@class="item-title"]//h2[contains(@class, "title")]/a/@href').extract()
        for href in href_list:
            yield scrapy.Request(
                url=href,
                callback=self.parse_company_overview
            )

    def parse_company_overview(self, response):
        item = CompanyItem()

        main_products = response.xpath('//tr[@data-role="supplierMainProducts"]/td[@class="col-value"]/a/text()').extract()
        if not main_products:
            main_products = response.xpath('//div[@class="detail-verified"]/div[contains(@class, "next-row")][3]'
                                           '/div[@class="item-value"]/a/text()').extract()
        item['main_products'] = main_products[0].strip() if main_products else None

        contact_person = re.search("contactName: '(.*?)'", response.body_as_unicode(), re.DOTALL)
        item['contact_person'] = contact_person.group(1) if contact_person else None

        contact_link = response.xpath('//ul[@class="navigation-list"]/li[4]/a/@href').extract()
        yield scrapy.Request(
            url=urljoin(response.url, contact_link[0]),
            callback=self.parse_company_contact,
            meta={'item': item}
        )

    def parse_company_contact(self, response):
        item = response.meta.get('item')

        company_name = response.xpath('//table[@class="contact-table"]/tr[1]/td/text()').extract()
        item['company_name'] = company_name[0] if company_name else None

        website = response.xpath('//table[@class="contact-table"]/tr[3]/td//text()').extract()
        item['website'] = ' '.join(website)

        country = response.xpath('//span[@class="location"]/text()').extract()
        item['country'] = country[0] if country else None

        yield item
