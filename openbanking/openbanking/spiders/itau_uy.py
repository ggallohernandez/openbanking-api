from datetime import datetime

from openbanking.items import Movement, AccountBalance

import scrapy
import locale

from scrapy_playwright.page import PageMethod
from bs4 import BeautifulSoup

class ItauUySpider(scrapy.Spider):
    name = "itau_uy"
    allowed_domains = ["itau.com.uy", "itaulink.com.uy"]
    start_urls = ['https://www.itau.com.uy/inst/']
    
    # Set setting in the init method
    def __init__(self, current="1", historical="0", *args, **kwargs):
        super(ItauUySpider, self).__init__(*args, **kwargs)
        
        locale.setlocale(locale.LC_NUMERIC, 'es_UY.UTF-8')
        
        self.current = True if current == "1" else False
        self.historical = True if historical == "1" else False
    
    # start requests
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta=dict(
                    playwright=True,
                    playwright_page_methods=[
                        #PageMethod("screenshot", path="1.png", full_page=True),
                    ]
                ),
                callback=self.parse,
            )

    def parse(self, response):
        # Find the login form and fill in the inputs with ID documento and ID pass
        yield scrapy.FormRequest.from_response(
            response,
            formid='acceso_hb',
            formdata={
                'tipo_documento': '1',
                'nro_documento': self.settings.get('ITAU_UY_CI'),
                'pass': self.settings.get('ITAU_UY_PASSWORD'),
                'tipo_usuario': 'R',
            },
            meta=dict(
                playwright=True,
                playwright_page_methods=[
                    #PageMethod("screenshot", path="2.png", full_page=True),
                ]
            ),
            callback=self.after_login,
        )

    def after_login(self, response):
        # Check if the login was successful
        account = response.css('.cuenta-numero::text').get()
        
        if account:
            self.logger.info("Login successful")
            # Extract some information from the dashboard page
            yield AccountBalance(
                account_number=account,
                balance=locale.atof(response.css('.saldo-valor::text').get().strip()),
            )
            
            for account_link in response.css('#cajasDeAhorro a'):
                yield response.follow(
                    account_link,
                    meta=dict(
                        playwright=True,
                        playwright_page_methods=[
                            #PageMethod("screenshot", path="3.png", full_page=True),
                        ]
                    ),
                    callback=self.after_select_account
                )
        else:
            self.logger.error("Login failed")
    
    def after_select_account(self, response):
        # Check if the login was successful
        account = response.css('.cuenta-numero::text').get()
        
        if account:
            self.logger.info(f"Selecting period for Account #{account}")
            # Extract somere information from the dashboard page
            
            if self.current:
                self.after_select_period(response)
            
            if self.historical:
                for option in response.css('#consultaHistorica select option::attr(value)')[1:]:
                    yield response.follow(
                        f'{response.url}?periodo={option.get()}',
                        meta=dict(
                            playwright=True,
                            playwright_page_methods=[
                                PageMethod("evaluate", "$('#consultaHistorica select').val('"+ option.get() +"').change()"),
                                PageMethod("wait_for_timeout", 500),
                            ]
                        ),
                        callback=self.after_select_period
                    )
        else:
            self.logger.error("Period selection failed")
    
    def after_select_period(self, response):
        account = response.css('.cuenta-numero::text').get()
        
        if account:
            self.logger.info(f"Account #{account} selected")
            # Extract somere information from the dashboard page
            
            for row in response.css('.table-cajas-de-ahorro tbody tr'):
                fields = row.css('td')
                soup = BeautifulSoup(fields[1].get())
                
                yield Movement(
                    account_number=account,
                    date=datetime.strptime(fields[0].css('::text').get().strip(), '%d-%m-%y').strftime('%Y-%m-%d') if fields[0].css('::text') else datetime.now().strftime('%y-%m-%d'),
                    description=soup.get_text().strip(),
                    amount=-locale.atof(fields[2].css('::text').get().strip()) if fields[2].css('::text') else (locale.atof(fields[3].css('::text').get().strip()) if fields[3].css('::text') else 0),
                    balance=locale.atof(fields[4].css('::text').get().strip()),
                )
        else:
            self.logger.error("Account selection failed")
    
    