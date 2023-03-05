# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from dataclasses import dataclass, field, asdict
from datetime import datetime

from openbanking.helpers import get_string_checksum


@dataclass(frozen=True)
class AccountBalance:
    account_number: str = field(hash=True)
    balance: float = field(hash=True)
    uid: str = field(hash=False, default='')
    source: str = field(hash=True, default='') 
    seen_at: str = field(hash=True, default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}
    
    def calculate_uid(self):
        string = f'{self.source}-{self.account_number}-{self.balance}-{self.seen_at}'
        return get_string_checksum(string)
        

@dataclass(frozen=True)
class Movement:
    account_number: str = field(hash=True, repr=True)
    amount: float = field(hash=True, repr=True)
    date: str = field(hash=True, repr=True)
    balance: float = field(hash=True, repr=True)
    uid:str = field(hash=False, repr=True, default='')
    source: str = field(hash=True, repr=True, default='')
    seen_at: str = field(hash=False, repr=False, default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    description: str = field(hash=True, repr=False, default='')
    
    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}
    
    def calculate_uid(self):
        string = f'{self.source}-{self.account_number}-{self.amount}-{self.date}-{self.balance}-{self.description}'
        return get_string_checksum(string)