# -*- coding: utf-8 -*-
import scrapy
from scrapy.http.request import Request
from CloudMusic.items import CloudmusicItem
import sys
import lxml


class CloudmusicSpider(scrapy.Spider):
    name = 'cloudmusic'
    baseurl = 'https://music.163.com/#/discover/playlist/?order=hot&cat=%E5%85%A8%E9%83%A8&limit={}&offset={}'
    # end = int(input("请输入需要爬取多少页："))
    end = 3

    def start_requests(self):
        for i in range(0, self.end):
            print("起始的歌单推荐页：", self.baseurl.format("35", str(i * 35)))
            yield scrapy.Request(self.baseurl.format("35", str(i * 35), dont_filter=True, callback=self.parse))

    def parse(self, response):
        # with open('1.html', "wb") as f:
        #     f.write(response.body)
        # 歌单推荐页数据
        # 歌单详情页数据
        links = response.xpath(
            '//ul[@id="m-pl-container"]/li//div/a[@class="msk"]/@href').extract()
        print(len(links))
        for link in links:
            item_list = CloudmusicItem()
            # 歌单id
            item_list['list_id'] = link.split('=')[1]
            # 歌单链接
            item_list['list_link'] = link
            url = 'https://music.163.com/#' + link
            yield scrapy.Request(url=url, dont_filter=True, callback=self.parse_list, meta={'item_list': item_list})

    def parse_list(self, response):
        print('歌单页：', response.url)
        # with open('2.html', "wb") as f:
        #     f.write(response.body)
        item_list = response.meta['item_list']
        # 歌单标题
        item_list['list_title'] = response.xpath(
            '//div[@class="tit"]/h2/text()').extract()[0]
        # 歌单图片链接
        item_list['list_img'] = response.xpath(
            '//div[@class="cover u-cover u-cover-dj"]/img/@data-src').extract()
        # 歌单作者
        item_list['list_author'] = response.xpath(
            '//div[@class="user f-cb"]/span/a/text()').extract()[0]
        # 歌单播放量
        item_list['list_amount'] = response.xpath(
            '//div[@class="n-songtb"]//strong/text()').extract()[0]
        # 歌单外链播放器 TODO
        # 歌单标签
        item_list['list_tags'] = response.xpath(
            '//div[@class="tags f-cb"]/a/i/text()').extract()
        # 歌单收藏量
        item_list['list_collection'] = response.xpath(
            '//div[@class="btns f-cb"]/a[3]/i/text()').extract()[0][1:-1]
        # 歌单分享量
        item_list['list_forward'] = response.xpath(
            '//div[@class="btns f-cb"]/a[4]/i/text()').extract()[0][1:-1]
        # 歌单评论数
        item_list['list_comment'] = response.xpath(
            '//div[@class="btns f-cb"]/a[6]/i/span/text()').extract()[0]
        # 歌单描述
        item_list['list_description'] = "\n".join(response.xpath(
            '//p[@id="album-desc-more"]/text()').extract())
        # 歌单里面的歌曲列表
        links = response.xpath(
            '//div[@id="m-playlist"]//div[@class="n-songtb"]//tr/td[2]//a/@href').extract()
        list_songs = []
        for link in links:
            song_id = link.split('=')[1]
            list_songs.append(song_id)
            item_song = CloudmusicItem()
            item_song['song_id'] = song_id
            item_song['song_link'] = link
            url = 'https://music.163.com/#' + link
            yield scrapy.Request(url, dont_filter=True, callback=self.parse_song, meta={'item_song': item_song})
        item_list['list_songs'] = list_songs
        # print(item_list)
        yield item_list

    def parse_song(self, response):
        print('歌曲页：', response.url)
        # with open('3.html', "wb") as f:
        #     f.write(response.body)
        item_song = response.meta['item_song']
        # 歌曲名
        item_song['song_name'] = response.xpath(
            '//div[@class="tit"]/em/text()').extract()[0]
        # 歌手名
        item_song['song_artist'] = response.xpath(
            '//p[@class="des s-fc4"]//a/text()').extract()[0]
        # 专辑名
        item_song['song_album'] = response.xpath(
            '//p[@class="des s-fc4"]//a/text()').extract()[1]
        # 歌词（可以通过歌曲id后面再爬取歌词）
        item_song['song_lyric'] = ''.join(response.xpath(
            '//div[@id="flag_more"]/text()').extract())
        # 歌曲评论数量
        item_song['song_comment'] = response.xpath(
            '//div[@class="m-info"]//span[@id="cnt_comment_count"]/text()').extract()[0]
        # 专辑图片链接
        item_song['song_albumPicture'] = response.xpath(
            '//img[@class="j-img"]/@data-src').extract()
        # 外链链接 TODO
        # print(item_song)
        yield item_song
