import scrapy


class CompanyItem(scrapy.Item):
    company_name = scrapy.Field()
    website = scrapy.Field()
    country = scrapy.Field()
    main_products = scrapy.Field()
    email_address = scrapy.Field()
    contact_person = scrapy.Field()
    contact_phone = scrapy.Field()
    skype = scrapy.Field()


class EuropagesItem(scrapy.Item):
    sector = scrapy.Field()
    country = scrapy.Field()
    company_name = scrapy.Field()
    website = scrapy.Field()
    keywords = scrapy.Field()
