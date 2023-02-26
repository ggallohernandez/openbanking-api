# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from dataclasses import dataclass
import datetime

@dataclass
class AccountBalance:
    account_number: str
    balance: float
    pass

@dataclass
class Movement:
    account_number: str
    date: datetime.datetime
    description: str
    amount: float
    balance: float
    pass