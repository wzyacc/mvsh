# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pdb
import pymongo
import hashlib
from elasticsearch import Elasticsearch

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

class Lol5sESPipeline(object):
    doc_type = 'mv_records'
    def __init__(self,es_uri, es_index):
        self.es_uri = es_uri
        self.es_index = es_index
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
                es_uri = crawler.settings.get('ES_URI'),
                es_index = crawler.settings.get('ES_INDEX','yse8') 
            )

    def open_spider(self,spider):
        self.es = Elasticsearch()
    
    def close_spider(self,spider):
        #self.es.close()
        pass

    def process_item(self, item, spider):
        item = dict(item)
        surl = item["surl"]
        ml = hashlib.md5()
        ml.update(surl.encode('utf-8'))
        _id = ml.hexdigest()
        try:
            old_item = self.es.get(index=self.es_index, doc_type=self.doc_type,id=_id)
        except Exception as e:
            old_item = None
            print e
        
        if not old_item:
            self.es.index(index=self.es_index, doc_type=self.doc_type, id=_id,body=item)
            return item
        old_item = old_item["_source"]
        if item["name"] != old_item["name"] or len(item["mv_plist"]) > len(old_item["mv_plist"]) or len(item["mv_dlist"]) > len(old_item["mv_dlist"]):
            try:
                self.es.update(index=self.es_index, doc_type=self.doc_type, id=_id,body=item)
            except Exception as e:
                self.es.index(index=self.es_index, doc_type=self.doc_type, id=_id,body=item)
        return None
