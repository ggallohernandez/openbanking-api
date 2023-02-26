from datetime import datetime

from openbanking.items import AccountBalance
from openbanking.items import Movement

import scrapy
import locale

from scrapy_playwright.page import PageMethod
from bs4 import BeautifulSoup

class ItauUySpider(scrapy.Spider):
    name = "itau_uy"
    allowed_domains = ["itau.com.uy", "itaulink.com.uy"]
    start_urls = ['https://www.itau.com.uy/inst/']
    
    # Set setting in the init method
    def __init__(self, *args, **kwargs):
        super(ItauUySpider, self).__init__(*args, **kwargs)
        
        locale.setlocale(locale.LC_NUMERIC, 'es_UY.UTF-8')

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, meta={'playwright': True})

    def parse(self, response):
        # Find the login form and fill in the inputs with ID documento and ID pass
        yield scrapy.FormRequest.from_response(
            response,
            formid='acceso_hb',
            formdata={
                'segmento': 'panelPersona',
                'tipo_documento': '1',
                'nro_documento': self.settings.get('ITAU_UY_CI'),
                'pass': self.settings.get('ITAU_UY_PASSWORD'),
                'password': self.settings.get('ITAU_UY_PASSWORD'),
                'id': 'login',
                'tipo_usuario': 'R',
                'bfpstatus': '5'
            },
            meta={'playwright': True},
            callback=self.after_login
        )

    def after_login(self, response):
        # Check if the login was successful
        account = response.css('.cuenta-numero::text').get().strip()
        
        if account:
            self.logger.info("Login successful")
            # Extract some information from the dashboard page
            yield AccountBalance(
                account_number=account,
                balance=locale.atof(response.css('.saldo-valor::text').get().strip()),
            )
            
            yield scrapy.Request(url=f"https://www.itaulink.com.uy{response.css('#cajasDeAhorro a::attr(href)').get()}", 
                                 meta={'playwright': True},
                                 callback=self.after_select_account)

        else:
            self.logger.error("Login failed")

    def after_select_account(self, response):
        account = response.css('.cuenta-numero::text').get().strip()
        
        if account:
            self.logger.info(f"Account #{account} selected")
            # Extract some information from the dashboard page
            
            for row in response.css('.table-cajas-de-ahorro tbody tr'):
                fields = row.css('td')
                soup = BeautifulSoup(fields[1].get())
                
                yield Movement(
                    account_number=account,
                    date=datetime.strptime(fields[0].css('::text').get().strip(), '%d-%m-%y') if fields[0].css('::text') else datetime.now(),
                    description=soup.get_text().strip(),
                    amount=-locale.atof(fields[2].css('::text').get().strip()) if fields[2].css('::text') else (locale.atof(fields[3].css('::text').get().strip()) if fields[3].css('::text') else 0),
                    balance=locale.atof(fields[4].css('::text').get().strip()),
                )
        else:
            self.logger.error("Account selection failed")