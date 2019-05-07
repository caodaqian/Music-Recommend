# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CloudmusicItem(scrapy.Item):
    # 歌单部分
    list_title = scrapy.Field()  # 歌单名
    list_id = scrapy.Field()    # 歌单id
    list_link = scrapy.Field()  # 歌单链接
    list_img = scrapy.Field()  # 歌单图片
    list_author = scrapy.Field()  # 歌单作者
    list_amount = scrapy.Field()  # 歌单播放量
    list_chain = scrapy.Field()  # 歌单外链播放器
    list_tags = scrapy.Field()  # 歌单的标签
    list_collection = scrapy.Field()  # 歌单收藏量
    list_forward = scrapy.Field()  # 歌单分享量
    list_comment = scrapy.Field()  # 歌单评论数
    list_description = scrapy.Field()  # 歌单描述
    list_songs = scrapy.Field()  # 歌曲（id形式）（/ song?id = 2489385)
    # 歌曲部分
    song_id = scrapy.Field()    # 歌曲id
    song_link = scrapy.Field()  # 歌曲链接
    song_name = scrapy.Field()  # 歌曲名
    song_artist = scrapy.Field()  # 歌手名
    song_album = scrapy.Field()  # 专辑名
    song_lyric = scrapy.Field()  # 歌词（可以通过歌曲id后面再爬取歌词）
    song_comment = scrapy.Field()  # 歌曲评论数量
    song_albumPicture = scrapy.Field()  # 专辑图片链接
    song_chain = scrapy.Field()  # 外链链接
