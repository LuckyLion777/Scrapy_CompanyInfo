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


class CompanyProductItem(scrapy.Item):
    # product_name = scrapy.Field()
    company_name = scrapy.Field()
    # category = scrapy.Field()
    # country = scrapy.Field()
    # country = scrapy.Field()
    website = scrapy.Field()
    # telephone = scrapy.Field()
    email = scrapy.Field()
    street_address_city = scrapy.Field()
    products = scrapy.Field()
    # contact_person = scrapy.Field()
    # skype = scrapy.Field()
    # link = scrapy.Field()
    # contact_person = scrapy.Field()
