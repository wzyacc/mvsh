# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
import hashlib

class Lol5SPipeline(object):
    tb_name = 'mv_records'
    def __init__(self,mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
                mongo_uri = crawler.settings.get('MONGO_URI'),
                mongo_db = crawler.settings.get('MONGO_DATABASE','yse8') 
            )

    def open_spider(self,spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
    def close_spider(self,spider):
        self.client.close()

    def process_item(self, item, spider):
        item = dict(item)
        surl = item["surl"]
        ml = hashlib.md5()
        ml.update(surl.encode('utf-8'))
        _id = ml.hexdigest()
        item['_id'] = ml.hexdigest()
        coll = self.db[self.tb_name]
        old_item = coll.find_one({'_id':_id})
        if not old_item:
            coll.insert_one(dict(item))
            return item
        if item["name"] != old_item["name"] or len(item["mv_plist"]) != len(old_item["mv_plist"]):
            del item['_id']
            coll.update({'_id':_id},{'$set':item})
        return None