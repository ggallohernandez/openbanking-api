from dataclasses import replace
from datetime import datetime
import locale
import unittest

from openbanking.items import AccountBalance, Movement
from openbanking.helpers import get_checksum
from openbanking.pipelines import HashItem
from openbanking.spiders.itau_uy import ItauUySpider

class TestHashingHelper(unittest.TestCase):
    
    def setUp(self):
        self.spider = ItauUySpider()
        self.pipeline = HashItem()
        
        locale.setlocale(locale.LC_NUMERIC, 'es_UY.UTF-8')
    
    def test_base(self):
        now = datetime.now().strftime('%Y-%m-%d')
        m1 = Movement(
            account_number='123',
            amount=100,
            balance=100,
            date=now,
            description='test'
        )
        
        m2 = Movement(
            account_number='123',
            amount=200,
            balance=300,
            date=now,
            description='test2'
        )
        
        m3 = Movement(
            account_number='123',
            amount=100,
            balance=100,
            date=now,
            description='test'
        )
        
        m1 = self.pipeline.process_item(m1, self.spider)
        m2 = self.pipeline.process_item(m2, self.spider)
        m3 = self.pipeline.process_item(m3, self.spider)
        
        self.assertEqual(m1.uid, m3.uid)
        self.assertNotEqual(m1.uid, m2.uid)
        
        b1 = AccountBalance(
            account_number='123',
            balance=100,
            seen_at=now
        )
        
        b2 = AccountBalance(
            account_number='123',
            balance=101,
            seen_at=now
        )
        
        b3 = AccountBalance(
            account_number='123',
            balance=100,
            seen_at=now
        )
        
        b1 = self.pipeline.process_item(b1, self.spider)
        b2 = self.pipeline.process_item(b2, self.spider)
        b3 = self.pipeline.process_item(b3, self.spider)
        
        self.assertEqual(b1.uid, b3.uid)
        self.assertNotEqual(b1.uid, b2.uid)

    def test_diff(self):
        m = Movement(
            account_number='123',
            amount=100,
            balance=100,
            date=datetime.now().strftime('%Y-%m-%d'),
            description='test'
        )
        
        m1 = self.pipeline.process_item(m, self.spider)
        
        self.assertNotEqual(self.pipeline.process_item(replace(m, amount=200), self.spider).uid, m1.uid)
        self.assertNotEqual(self.pipeline.process_item(replace(m, balance=200), self.spider).uid, m1.uid)
        self.assertNotEqual(self.pipeline.process_item(replace(m, description='test2'), self.spider).uid, m1.uid)
        self.assertNotEqual(self.pipeline.process_item(replace(m, date=datetime.now()), self.spider).uid, m1.uid)
        self.assertNotEqual(self.pipeline.process_item(replace(m, account_number='1234'), self.spider).uid, m1.uid)

        b = AccountBalance(
            account_number='123',
            balance=100
        )
        
        b1 = self.pipeline.process_item(b, self.spider)
        
        self.assertNotEqual(self.pipeline.process_item(replace(b, account_number='1234'), self.spider).uid, b1.uid)
        self.assertNotEqual(self.pipeline.process_item(replace(b, balance=200), self.spider).uid, b1.uid)
        self.assertNotEqual(self.pipeline.process_item(replace(b, seen_at=datetime.strptime('2020-01-01', '%Y-%m-%d').strftime('%y-%m-%d %H:%M:%S')), self.spider).uid, b1.uid)

    def test_optionals(self):
        m = Movement(
            account_number='123',
            amount=100,
            balance=100,
            date=datetime.now().strftime('%Y-%m-%d'),
            description='test'
        )
        
        m1 = self.pipeline.process_item(m, self.spider)
        
        self.assertEqual(self.pipeline.process_item(replace(m, uid="testme"), self.spider).uid, m1.uid)
        self.assertEqual(self.pipeline.process_item(replace(m, seen_at=datetime.now().strftime('%Y-%m-%s %H:%M:%S')), self.spider).uid, m1.uid)
        
        now = datetime.now()
        
        b = AccountBalance(
            account_number='123',
            balance=100,
            seen_at=now.strftime('%Y-%m-%d %H:%M:%S')
        )
        
        b1 = self.pipeline.process_item(b, self.spider)
        
        self.assertEqual(self.pipeline.process_item(replace(b, uid="testme"), self.spider).uid, b1.uid)

    def test_checksum(self):
        now=datetime.now().strftime('%Y-%m-%d')
        m1 = Movement(
            account_number='123',
            amount=100,
            balance=100,
            date=now,
            description='test'
        )
        
        m2 = Movement(
            account_number='123',
            amount=100,
            balance=100,
            date=now,
            description='test'
        )
        
        self.assertEqual(get_checksum(m1), get_checksum(m2))
        
        m1 = Movement(
            account_number='123',
            amount=100,
            balance=100,
            date=datetime.strptime('02-03-23', '%d-%m-%y').strftime('%Y-%m-%d'),
            description='hello world'
        )
        
        m2 = Movement(
            account_number='123',
            amount=100,
            balance=100,
            date=datetime.strptime('02-03-23', '%d-%m-%y').strftime('%Y-%m-%d'),
            description='hello world'
        )
        
        self.assertEqual(get_checksum(m1), get_checksum(m2))


if __name__ == '__main__':
    unittest.main()