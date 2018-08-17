import scrapy
import re
from Scrapy_CompanyInfo.items import CompanyProductItem
from urllib.parse import urljoin


class SiepaCrawler(scrapy.Spider):
    name = 'siepa_crawler'
    allowed_domains = ['crm.siepa.gov.rs']
    start_urls = ['http://crm.siepa.gov.rs/suppliers-eng/']
    unique_company_list = set()
    unique_cat_list = set()

    def parse(self, response):
        show_more_link = response.xpath('//a[contains(text(), "SHOW MORE")]/@href').extract_first()
        if show_more_link:
            yield scrapy.Request(
                url=urljoin(response.url, show_more_link),
                callback=self.parse
            )
        else:
            company_link_list = response.xpath('//a[@class="cut"]/@href').extract()
            for com_link in company_link_list:
                if (com_link not in self.unique_company_list) and ('limit=' not in com_link):
                    self.unique_company_list.add(com_link)
                    yield scrapy.Request(
                        url=urljoin(response.url, com_link),
                        callback=self.parse_company_info
                    )

            category_link_list = response.xpath('//a[@class="amsll"]/@href').extract()
            for cat_link in category_link_list:
                if cat_link not in self.unique_cat_list:
                    self.unique_cat_list.add(cat_link)
                    yield scrapy.Request(
                        url=urljoin(response.url, cat_link),
                        callback=self.parse
                    )

        # yield scrapy.Request(
        #     url='http://crm.siepa.gov.rs/suppliers-eng/supplier.php?ID=1813',
        #     callback=self.parse_company_info
        # )

    def parse_company_info(self, response):
        item = CompanyProductItem()
        item['company_name'] = response.xpath('//table[@width="780"]/tr[8]/td[1]//div[1]/div[4]/text()').extract_first()
        item['country'] = response.xpath('//table[@width="780"]/tr[8]/td[1]//div[1]/div[24]/text()').extract_first()
        item['website'] = response.xpath('//table[@width="780"]/tr[12]/td[1]/div[1]/div[32]/a/@href').extract_first()
        item['telephone'] = response.xpath('//table[@width="780"]/tr[12]/td[1]/div[1]/div[20]/text()').extract_first()
        item['email'] = response.xpath('//table[@width="780"]/tr[12]/td[1]/div[1]/div[28]/a/text()').extract_first()
        item['products'] = response.xpath('//table[@width="780"]/tr[35]/td[1]/div[1]//h5/text()').extract()
        if not item['products']:
            item['products'] = response.xpath('//table[@width="780"]/tr[37]/td[1]/div[1]//h5/text()').extract()
        contact_person = response.xpath('//table[@width="780"]/tr[32]/td[1]/div[1]//text()').extract()
        contact_list = []
        for p in contact_person:
            if p.strip() and 'Contacts:' not in p:
                contact_list.append(p.strip().replace('-', '').replace('Contact person', '').strip())
        item['contact_person'] = contact_list

        yield item