from datetime import datetime

from openbanking-api.app.openbanking.items import AccountBalance

from openbanking-api.app.openbanking.items import Movement
import scrapy
from scrapy_splash import SplashFormRequest
import locale

account_chooser="""
function main(splash)
    splash:wait(1)
    splash:runjs('document.querySelector("#cajasDeAhorro a").click()')
    splash:wait(1)
    return {
        html = splash:html(),
    }
end
"""

class ItauUySpider(scrapy.Spider):
    name = "itau_uy"
    allowed_domains = ["itau.com.uy", "itaulink.com.uy"]
    start_urls = ['https://www.itau.com.uy/inst/']
    
    # Set setting in the init method
    def __init__(self, *args, **kwargs):
        super(ItauUySpider, self).__init__(*args, **kwargs)
        
        if self.settings.get('ITAU_UY_CI', None) is None:
            raise ValueError('ITAU_UY_CI setting is required')
        
        if self.settings.get('ITAU_UY_PASSWORD', None) is None:
            raise ValueError('ITAU_UY_PASSWORD setting is required')
        
        locale.setlocale(locale.LC_NUMERIC, 'es_UY.UTF-8')

    def parse(self, response):
        # Find the login form and fill in the inputs with ID documento and ID pass
        return SplashFormRequest.from_response(
            response,
            formid='acceso_hb',
            formdata={
                'tipo_documento': '1',
                'nro_documento': self.settings.get('ITAU_UY_CI'),
                'pass': self.settings.get('ITAU_UY_PASSWORD'),
                'id': 'login',
                'tipo_usuario': 'R'
            },
            callback=self.after_login
        )

    def after_login(self, response):
        # Check if the login was successful
        account = response.css('.cuenta-numero').get()
        
        if account:
            self.logger.info("Login successful")
            # Extract some information from the dashboard page
            yield AccountBalance({
                'account': response.css('.cuenta-numero').get(),
                'balance': locale.atof(response.css('.saldo-valor').get()),
            })
            
            return SplashFormRequest.from_response(
                response,
                args = {'lua_source': account_chooser, 'timeout': 5},
                callback=self.after_select_account
            )
        else:
            self.logger.error("Login failed")

    def after_select_account(self, response):
        account = response.css('.cuenta-numero').get()
        
        if account:
            self.logger.info(f"Account #{account} selected")
            # Extract some information from the dashboard page
            
            for row in response.css('.table-cajas-de-ahorro tr'):
                fields = row.css('td').getall()
                yield Movement({
                    'account': account,
                    'date': datetime.strptime(fields[0], '%d-%m-%y').date(),
                    'description': fields[1],
                    'amount': -locale.atof(fields[2]) if fields[2] else locale.atof(fields[3]),
                    'balance': locale.atof(fields[4]),
                })
        else:
            self.logger.error("Account selection failed")