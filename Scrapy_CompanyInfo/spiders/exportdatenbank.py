import scrapy
from Scrapy_CompanyInfo.items import CompanyProductItem
from urllib.parse import urljoin


class ExportdatenbankCrawler(scrapy.Spider):
    name = 'export_crawler'
    allowed_domains = ['www.deutsche-exportdatenbank.de']
    start_urls = ['https://www.deutsche-exportdatenbank.de/eng/']
    unique_data = set()

    def parse(self, response):
        href_list = response.xpath('//ul[@id="nomenklaturliste"]/ul/li/span/a/@href').extract()
        for i in range(len(href_list)):
            yield scrapy.Request(
                url=urljoin(response.url, href_list[i]),
                callback=self.parse_main_category,
                meta={'cat_num': i+1}
            )

    def parse_main_category(self, response):
        num = response.meta.get('cat_num')
        xpath = '//ul[@id="nomenklaturliste"]/ul/li[%d]/ul/li/span/a/@href'
        href_list = response.xpath(xpath % num).extract()
        for i in range(len(href_list)):
            response.meta.update({'sub_num': i+1})
            yield scrapy.Request(
                url=urljoin(response.url, href_list[i]),
                callback=self.parse_sub_category,
                meta=response.meta
            )

    def parse_sub_category(self, response):
        num = response.meta.get('cat_num')
        sub_num = response.meta.get('sub_num')
        xpath = '//ul[@id="nomenklaturliste"]/ul/li[%d]/ul/li[%d]/ul/li/span/a/@href'
        href_list = response.xpath(xpath % (num, sub_num)).extract()
        for i in range(len(href_list)):
            response.meta.update({'last_num': i + 1})
            yield scrapy.Request(
                url=urljoin(response.url, href_list[i]),
                callback=self.parse_last_category,
                meta=response.meta
            )

    def parse_last_category(self, response):
        num = response.meta.get('cat_num')
        sub_num = response.meta.get('sub_num')
        last_num = response.meta.get('last_num')
        xpath = '//ul[@id="nomenklaturliste"]/ul/li[%d]/ul/li[%d]/ul/li[%d]/ul/li/span/a/@href'
        href_list = response.xpath(xpath % (num, sub_num, last_num)).extract()
        for i in range(len(href_list)):
            yield scrapy.Request(
                url=urljoin(response.url, href_list[i]),
                callback=self.parse_detail_link
            )

    def parse_detail_link(self, response):
        href_list = response.xpath('//ul[@id="trefferliste"]/li/div/h4/a/@href').extract()
        for href in href_list:
            yield scrapy.Request(
                url=urljoin(response.url, href),
                callback=self.parse_detail
            )

    def parse_detail(self, response):
        item = CompanyProductItem()
        item['company_name'] = response.xpath('//div[@id="firmenprofil"]/h1/span/text()').extract_first().strip()
        item['website'] = response.xpath('//div[@id="firmenprofil"]'
                                         '/h4[@class="kontakt fpurls"]/div/span/a/text()').extract_first()
        item['email'] = response.xpath('//div[@id="firmenprofil"]'
                                       '/h4[contains(@class, "openParent")]/span/a/text()').extract_first()
        street = response.xpath('//h4[@class="fpkontakt"]/span[@class="bold"]/text()').extract_first()
        town = response.xpath('//h4[@class="fpkontakt"]/text()[last()]').extract_first()
        item['street_address_city'] = street.strip() + town.strip()
        item['products'] = response.xpath('//ul[@id="fpdatalist"]/li/p/a/text()').extract()

        yield item