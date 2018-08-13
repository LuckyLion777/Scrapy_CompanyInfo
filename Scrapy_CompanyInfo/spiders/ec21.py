import scrapy
import math
import re
from Scrapy_CompanyInfo.items import CompanyItem
from urllib.parse import urljoin


class AlibabaCrawler(scrapy.Spider):
    name = 'ec21_crawler'
    allowed_domains = ['ec21.com']
    start_urls = ['https://www.ec21.com/companies/']
    unique_data = set()
    HEADER = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/68.0.3440.84 Safari/537.36'
    }

    def start_requests(self):
        yield scrapy.Request(
            url=self.start_urls[0],
            callback=self.parse,
            headers=self.HEADER
        )

    def parse(self, response):
        cat_list = response.xpath('//div[@class="view_buy_leads"]'
                                  '//dl[@class="posted_v_list"]/dt/a/@href').extract()
        for cat in cat_list:
            yield scrapy.Request(
                url=urljoin(response.url, cat),
                callback=self.parse_categories,
                headers=self.HEADER,
                dont_filter=True
            )

    def parse_categories(self, response):
        type_list = response.xpath('//div[@id="category"]//li/a/@href').extract()
        for type in type_list:
            yield scrapy.Request(
                url=type,
                callback=self.parse_types,
                headers=self.HEADER,
                dont_filter=True
            )

    def parse_types(self, response):
        views = response.xpath('//span[@class="viewTxt"]/text()').extract()
        total_count = re.search('of (.*)', views[0].replace(')', ''), re.DOTALL)
        total_count = int(total_count.group(1).replace(',', '')) if total_count else 0
        count_per_page = re.search('(.*?) out of', views[0], re.DOTALL)
        count_per_page = int(count_per_page.group(1).split('-')[1]) if count_per_page else 0

        page_url = response.url.replace('.html', '') + '/page-{page_num}.html'

        for i in range(math.ceil(total_count / count_per_page)):
            yield scrapy.Request(
                url=page_url.format(page_num=str(i+1)),
                callback=self.parse_pages,
                headers=self.HEADER,
                dont_filter=True
            )

    def parse_pages(self, response):
        href_list = response.xpath('//div[@class="conProduct_list companyList"]'
                                   '//h2[@class="inlineTitle"]/a/@href').extract()
        name_list = response.xpath('//div[@class="conProduct_list companyList"]'
                                   '//h2[@class="inlineTitle"]/a/text()').extract()
        for i in range(len(href_list)):
            item = CompanyItem()
            item['company_name'] = name_list[i]
            if href_list[i] and href_list[i] not in self.unique_data:
                self.unique_data.add(href_list[i])
                yield scrapy.Request(
                    url=href_list[i],
                    callback=self.parse_company,
                    dont_filter=True,
                    headers=self.HEADER,
                    meta={'item': item}
                )

    def parse_company(self, response):
        item = response.meta.get('item')

        website = response.xpath('//ul[@class="script_box3"]//span[contains(text(), "- Website")]'
                                 '/following-sibling::span/text()').extract()
        if website and website[0] != '-':
            item['website'] = website[0]
        if not website:
            website = re.search('<br />Web:(.*?)<', response.body_as_unicode().replace('&nbsp;', ''), re.DOTALL)
            if website:
                item['website'] = website.group(1)

        country = response.xpath('//ul[@class="script_box3"]//span[contains(text(), "- Country/Region")]'
                                 '/following-sibling::span/text()').extract()
        if not country:
            country = response.xpath('//span[contains(text(), "CountryRegion")]'
                                    '/following-sibling::text()').extract()
        if not country:
            country = response.xpath('//td[@class="data"]//div[@class="databox"]'
                                     '/table/tr[1]/td/div/text()[2]').extract()
        item['country'] = country[0].strip().replace('[', '').replace(']', '') if country else None

        contact_person = response.xpath('//ul[@class="script_box3"]//span[contains(text(), "- Contact")]'
                                        '/following-sibling::span/text()').extract()
        if not contact_person:
            contact_person = response.xpath('//strong[contains(text(), "Contact")]'
                                            '/following-sibling::text()').extract()
        if not contact_person:
            contact_person = response.xpath('//th[contains(text(), "Contact")]'
                                            '/following-sibling::td[1]/text()').extract()
        item['contact_person'] = contact_person[0].strip() if contact_person else None

        contact_phone = response.xpath('//ul[@class="script_box3"]//span[contains(text(), "- Phone")]'
                                       '/following-sibling::span/text()').extract()
        if not contact_phone:
            contact_phone = response.xpath('//strong[contains(text(), "Phone")]'
                                           '/following-sibling::text()').extract()
        if not contact_phone:
            contact_phone = response.xpath('//th[contains(text(), "Phone")]'
                                           '/following-sibling::td[1]/text()').extract()
        item['contact_phone'] = contact_phone[0].strip().replace('\t', '').replace('\n', '') if contact_phone else None

        email_address = re.search('<br />Email:(.*?)<', response.body_as_unicode().replace('&nbsp;', ''), re.DOTALL)
        item['email_address'] = email_address.group(1) if email_address else None

        skype = re.search('<br />Skype:(.*?)<', response.body_as_unicode().replace('&nbsp;', ''), re.DOTALL)
        item['skype'] = skype.group(1) if skype else None

        main_products = response.xpath('//ul[@class="script_box3"]//span[contains(text(), "- Selling Categories")]'
                                       '/following-sibling::span[1]/a/text()').extract()
        if not main_products:
            main_products = response.xpath('//td[@class="LM"]//tr/td[4]/a/text()').extract()
        item['main_products'] = ', '.join(main_products)

        yield item
