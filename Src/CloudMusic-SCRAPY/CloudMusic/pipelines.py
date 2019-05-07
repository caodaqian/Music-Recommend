# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import os

DATA_PATH = 'G:\Coding Project\Music Recommendation System\Data\\'

class CloudmusicPipeline(object):
    def process_item(self, item, spider):
        print(item)
        # 歌单部分
        if item.get('list_id') != None:
            with open(DATA_PATH + 'lists.json', 'a') as f:
                f.write(json.dumps(dict(item), ensure_ascii=False) + ",\n")
                f.flush()
        if item.get('song_id') != None:
            with open(DATA_PATH + 'songs.json', 'a') as f:
                f.write(json.dumps(dict(item), ensure_ascii=False) + ",\n")
                f.flush()
