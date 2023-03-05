# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass(frozen=True)
class AccountBalance:
    account_number: str = field(hash=True)
    balance: float = field(hash=True)
    uid: str = field(hash=False, default='')
    source: str = field(hash=True, default='') 
    seen_at: datetime = field(hash=True, default=datetime.now())
    
    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}
        

@dataclass(frozen=True)
class Movement:
    account_number: str = field(hash=True)
    amount: float = field(hash=True)
    date: datetime = field(hash=True)
    balance: float = field(hash=True)
    uid:str = field(hash=False, default='')
    source: str = field(hash=True, default='')
    seen_at: datetime = field(hash=False, default=datetime.now())
    description: str = field(hash=True, default='')
    
    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}