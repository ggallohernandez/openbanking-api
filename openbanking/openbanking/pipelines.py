# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from datetime import datetime
from itemadapter import ItemAdapter
from google.api_core import retry
from openbanking.helpers import dict_hash, get_checksum
from scrapy.exceptions import DropItem
from google.cloud import bigquery
from dataclasses import replace

from openbanking.items import Movement, AccountBalance


class HashItem:
    def process_item(self, item, spider):
        c = replace(item, source=spider.name)
        return replace(c, uid=c.calculate_uid())

class DedupItems:
    def __init__(self):
        self.client = bigquery.Client()

    def process_item(self, item, spider):
        if isinstance(item, Movement):
            query = """
                SELECT uid
                FROM `openbanking-379605.openbanking.account_movements`
                WHERE uid = @uid
            """
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("uid", "STRING", item.uid),
                ]
            )
            query_job = self.client.query(query, job_config=job_config)  # Make an API request.

            if query_job.result().total_rows:
                raise DropItem("Duplicate item found: %s" % item)
        elif isinstance(item, AccountBalance):
            query = """
                SELECT uid
                FROM `openbanking-379605.openbanking.account_balances`
                WHERE uid = @uid
            """
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("uid", "STRING", item.uid),
                ]
            )
            query_job = self.client.query(query, job_config=job_config)  # Make an API request.

            if query_job.result().total_rows:
                raise DropItem("Duplicate item found: %s" % item)
        else:
            raise DropItem("Unknown item type: %s" % item)

        return item
    
class UploadToBigQuery:
    def __init__(self):
        self.client = bigquery.Client()
    
    def process_item(self, item, spider):
        if isinstance(item, Movement):
            self.client.insert_rows_json('openbanking-379605.openbanking.account_movements', [item.dict()], retry=retry.Retry(timeout=30))
        elif isinstance(item, AccountBalance):
            self.client.insert_rows_json('openbanking-379605.openbanking.account_balances', [item.dict()], retry=retry.Retry(timeout=30))
        else:
            raise DropItem("Unknown item type: %s" % item)
        
        return item
