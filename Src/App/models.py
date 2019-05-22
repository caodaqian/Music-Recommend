# 用户管理模块
from Src.App.ext import StdError, ConnectMysql, Pages
from Src.App.settings import SCRAPY_PATH, MUSIC_PATH, RATE_PATH, CHROMEDRIVER_PATH, SCORE, RECOMMEND_PATH, ALGO_OPT, READER_OPT, RECOMMEND_NUM
from collections import defaultdict
from surprise import KNNBasic, Reader, Dataset
from surprise import dump
import re
import requests
import time
import pymysql
import os
import json
import hashlib
import sys


# 用户管理模块
class UserManager(object):
    def __init__(self):
        self.conn = ConnectMysql.new_connect()
        self.superpwd = 'cdq'

    def __del__(self):
        self.conn.close()

    def is_super(self, uid: int):
        ret = ConnectMysql.is_user_super(self.conn, uid)
        return ret

    def register(self, userName, userPwd, userSUPER, userEmail, userLikes=[]):
        # 创建用户信息
        userPwd = userPwd.encode('utf-8')
        userPwd = hashlib.md5(userPwd).hexdigest()
        # 验证管理员密钥
        if userSUPER == self.superpwd:
            userSUPER = 1
        else:
            userSUPER = 0
        return ConnectMysql.user_register(self.conn, userName, userPwd, userSUPER, userEmail, userLikes)

    def login(self, userName, userPwd):
        userPwd = hashlib.md5(userPwd.encode()).hexdigest()
        ret = ConnectMysql.user_login(self.conn, userName, userPwd)
        if ret != -1:
            cookie = {'user_id': ret, 'user_name': userName}
        else:
            cookie = None
        return cookie

    def forget_passwd(self, userName, userEmail, userNewPwd):
        userNewPwd = hashlib.md5(userNewPwd.encode()).hexdigest()
        return ConnectMysql.user_forget_passwd(self.conn, userName, userEmail, userNewPwd)


# 音乐上传模块
class UploadMusic(object):
    def __init__(self):
        self.conn = ConnectMysql.new_connect()

    def __del__(self):
        self.conn.close()

    @staticmethod
    def handle_json(data):
        # 处理一下song_lyric里面存在\\的问题
        if 'song_lyric' in data.keys():
            data['song_lyric'] = eval(
                repr(data['song_lyric']).replace(r"\\", ''))
        # 处理一下collection里面的**万问题
        if 'list_collection' in data.keys():
            index = data['list_collection'].find('万')
            data['list_collection'] = int(
                data['list_collection'][:index]) * 10000
        # 处理没有评论时候爬虫爬取的是“评论”的问题
        if 'song_comment' in data.keys() and data['song_comment'] == '评论':
            del data['song_comment']
        return data

    def upload_list(self, data):
        keys, vals = '', ''
        for kv in data.items():
            key = str(kv[0])
            keys += key + ','
            if key in ['list_id', 'list_amount', 'list_collection', 'list_forward', 'list_comment']:
                vals += str(kv[1]).replace('\'', r'\'') + ','
            else:
                vals += '\'' + str(kv[1]).replace('\'', r'\'') + '\','
        keys = keys[:-1]
        vals = vals[:-1]
        vals = vals.replace("\n", r'\n')
        vals = vals.replace("\t", r'\t')
        return ConnectMysql.upload_list(self.conn, keys, vals, data['list_id'])

    def upload_music(self, data):
        # 将歌单的标签加入到歌曲的属性当中
        songTags = ConnectMysql.get_tags_from_list(self.conn, data['song_id'])
        if songTags != '':
            data['song_tags'] = songTags
        # 导入进数据库
        keys, vals = '', ''
        for kv in data.items():
            key = str(kv[0])
            keys += key + ','
            if key in ['song_id', 'song_comment']:
                vals += str(kv[1]).replace('\'', r'\'') + ','
            else:
                vals += '\'' + str(kv[1]).replace('\'', r'\'') + '\','
        keys = keys[:-1]
        vals = vals[:-1]
        vals = vals.replace("\n", r'\n')
        vals = vals.replace("\t", r'\t')
        return ConnectMysql.upload_song(self.conn, keys, vals, data['song_id'])

    def __upload_file(self, filepath):
        try:
            fp = open(filepath, 'r', encoding='utf-8')
            while True:
                line = fp.readline()[:-2]
                if line == '':
                    break
                data = json.loads(line, encoding='utf-8')
                # 对scrapy爬出来文件有些错误进行处理
                data = UploadMusic.handle_json(data)
                # 对list和song进行单独的处理
                if 'list_id' in data.keys():
                    if self.upload_list(data):
                        StdError.info('list_id=%s已导入' % data['list_id'])
                elif 'song_id' in data.keys():
                    if self.upload_song(data):
                        StdError.info('song_id=%s已导入' % data['song_id'])
                else:
                    StdError.warn("上传模块出错\tjson文件中缺乏必要的id，line=" + line)
        except FileNotFoundError:
            self.conn.rollback()
            StdError.error('上传模块出错\t文件不存在，请调用scrapy爬虫创建数据文件')
        except UnicodeDecodeError:
            self.conn.rollback()
            StdError.error('上传模块出错\t文件格式不能正常解析，请调用scrapy爬虫创建数据文件')
        except json.decoder.JSONDecodeError:
            self.conn.rollback()
            StdError.error('上传模块出错\tjson文件不能解析，需要创建符合格式的json文件（参照Data文件夹下的json）')
        except Exception:
            self.conn.rollback()
            StdError.error('上传模块出出现未知错误\tline=' + line)

    def import_scrapy_data(self):
        file1, file2 = SCRAPY_PATH + "lists.json", SCRAPY_PATH + "songs.json"
        self.__upload_file(file1)
        self.__upload_file(file2)


# 打分模块
class Rate():
    def __init__(self):
        self.conn = ConnectMysql.new_connect()

    def __del__(self):
        self.conn.close()

    @staticmethod
    def dump2file(uid, sid, score):
        with open(RATE_PATH, 'a') as f:
            f.write("{},{},{},{}\n".format(uid, sid, score, time.time()))
            f.flush()

    def __score_action(self, like, unlike, audition, download):
        # 用户行为
        sLike = like * SCORE['like']
        sUnlike = unlike * SCORE['unlike']
        sAudition = audition * SCORE['audition']
        sDownload = download * SCORE['download']
        return sLike + sUnlike + sAudition + sDownload

    def __score_similar(self, uid, sid):
        # 标签类似
        userLike = ConnectMysql.get_user_tags(self.conn, uid)
        songTags = ConnectMysql.get_song_tags(self.conn, sid)
        if userLike == None:
            return 0
        elif songTags == None:
            return 0
        else:
            uLikeSet = set()
            for i in userLike:
                uLikeSet.add(i)
            sLikeSet = set()
            for i in songTags:
                sLikeSet.add(i)
            if sLikeSet.issubset(uLikeSet):
                return 2
            else:
                return -2

    def __score_comment(self, sid):
        comment = ConnectMysql.get_song_comment(self.conn, sid)
        return comment / SCORE['comment_base'] * SCORE['comments']

    def score(self, uid, sid, like, unlike, audition, download):
        sAction = self.__score_action(like, unlike, audition, download)
        sSimilar = self.__score_similar(uid, sid)
        sComment = self.__score_comment(sid)
        score = sAction + sSimilar + sComment
        StdError.info("行为得分={},标签得分={},热度得分={},最终得分={}".format(sAction, sSimilar, sComment, score))
        self.dump2file(uid, sid, score)

    def dump_from_db(self):
        actions = ConnectMysql.get_actions(self.conn)
        if actions != None and len(actions) > 0:
            os.remove(RATE_PATH)
            with open(RATE_PATH, 'w') as f:
                for aid, uid, sid, like, unlike, audition, download in actions:
                    sAction = self.__score_action(like, unlike, audition, download)
                    sSimilar = self.__score_similar(uid, sid)
                    sComment = self.__score_comment(sid)
                    score = sAction + sSimilar + sComment
                    f.write("{},{},{},{}\n".format(uid, sid, score, time.time()))
                    f.flush()


# 音乐检索模块
class MusicSearch(object):
    def __init__(self):
        self.MusicsearchAPI = 'http://music.163.com/api/search/get'
        self.headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip,deflate,sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,gl;q=0.6,zh-TW;q=0.4',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'music.163.com',
            'Referer': 'http://music.163.com/search/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36'
        }
        self.conn = ConnectMysql.new_connect()

    def __del__(self):
        self.conn.close()

    # 搜索单曲(1)，歌手(100)，专辑(10)，歌单(1000)，用户(1002) *(type)*
    def get_music_by_netcloud(self, s, stype=1, offset=0, total='true', limit=10):# TODO
        data = {
            'type': stype,
            'offset': offset,
            'total': total,
            'limit': limit,
            's': s
        }
        response = requests.post(self.MusicsearchAPI, data=data, headers=self.headers)
        pass

    def get_music_by_text(self, text):
        ret = ConnectMysql.get_songs_by_search(self.conn, text)
        return json.dumps(ret)


# 音乐推荐模块
class MusicRecommend():
    def __init__(self):
        self.current = 0
        self.updateTimeStamp = [(self.current, time.time())]
        self.top_n = defaultdict(list)
        reader = Reader(line_format=READER_OPT["line_format"], sep=READER_OPT["sep"],
                        rating_scale=READER_OPT["rating_scale"], skip_lines=READER_OPT["skip_lines"])
        self.data = Dataset.load_from_file(RATE_PATH, reader=reader)
        if os.path.isfile(RECOMMEND_PATH):
            self.predictions, self.algo = dump.load(RECOMMEND_PATH)
        else:
            sim_opt = {
                "name": ALGO_OPT["similarity"],
                "user_based": ALGO_OPT["user_based"]
            }
            self.algo = KNNBasic(sim_options=sim_opt)
            self.predictions = []

    def __del__(self):
        # dump.dump(RECOMMEND_PATH, predictions=self.predictions, algo=self.algo, verbose=0)
        StdError.info('The dump has been saved as file {}'.format(RECOMMEND_PATH))

    def calculate(self, n=100):
        trainset = self.data.build_full_trainset()
        self.algo.fit(trainset)
        testset = trainset.build_anti_testset()
        self.predictions = self.algo.test(testset)
        self.current += 1
        self.updateTimeStamp.append((self.current, time.time()))
        self.top_n = defaultdict(list)
        for uid, iid, t_rating, est, _ in self.predictions:
            self.top_n[uid].append((iid, est))
        for uid, user_ratings in self.top_n.items():
            user_ratings.sort(key=lambda x: x[1], reverse=True)
            self.top_n[uid] = user_ratings[:n]
        return (self.predictions, self.top_n)

    def get_top_n(self, uid, start=0, end=RECOMMEND_NUM):
        tmplist = self.top_n[str(uid)][start:end]
        return [iid for iid,_ in tmplist]

    def show(self):
        if self.current > 0:
            StdError.info("recommend current version={}".format(self.current))
            for uid, user_ratings in self.top_n.items():
                StdError.info(str(uid) + ":" + str([iid for iid,_ in user_ratings]))


# 音乐管理模块
class MusicManager():
    def __init__(self, mr=None):
        self.DownloadAPI = 'http://music.163.com/song/media/outer/url?id={}'
        self.conn = ConnectMysql.new_connect()
        self.SongURL = 'http://music.163.com'
        self.recommend = mr

    def __del__(self):
        self.conn.close()

    @staticmethod
    def is_in_set(sid, idset:set):
        if sid in idset:
            return True
        else:
            idset.add(sid)
            return False

    def get_recommend(self, uid, offset=0, limit=50, topk=RECOMMEND_NUM):  #TODO 推荐算法
        if (self.recommend == None):
            StdError.error("MusicManager模块没有传入recommend对象")
            return None
        start = offset * limit
        end = (offset + 1) * limit
        if end > topk:
            StdError.error("请求推荐超出限制！end={}，topk={}".format(limit, topk))
            return None
        # 获取真实推荐歌曲
        sidlist = self.recommend.get_top_n(uid, start, end)
        ret = []
        songSet = set()
        for i in sidlist:
            data = ConnectMysql.get_song_by_id(self.conn, i)
            if data != None:
                songSet.add(data[0])
                ret.append(data)
        topk -= len(sidlist)
        # 获取相似类型歌曲
        if topk > 0:
            tagsList = ConnectMysql.get_user_tags(self.conn, uid)
            if tagsList != None:
                songsList = ConnectMysql.get_songs_by_tags(self.conn, tagsList, topk)
                for songInfo in songsList:
                    songId = songInfo[0]
                    if not self.is_in_set(songId, songSet):
                        ret.append(songInfo)
                topk -= len(songsList)
        # 获取随即推荐歌曲
        if topk > 0:
            songsList = ConnectMysql.get_songs_by_random(self.conn, RECOMMEND_NUM * 2)
            for songInfo in songsList:
                songId = songInfo[0]
                if not self.is_in_set(songId, songSet):
                    ret.append(songInfo)
        ret = json.dumps(list(ret), ensure_ascii=False)
        return ret

    def get_music_info(self, sid):
        data = ConnectMysql.get_song_info(self.conn, sid)
        data = json.dumps(list(data), ensure_ascii=False)
        return data

    def get_music_num(self):
        data = ConnectMysql.get_music_number(self.conn)
        data = json.dumps({'number': data})
        return data

    def get_all_music(self, query:int, offset:int):
        start = (query - 1) * 16
        ret = {}
        data = ConnectMysql.get_all_music(self.conn, start, offset)
        ret['data'] = data
        page = Pages()
        page = page.check_and_ret(query, offset)
        ret['page'] = page
        return json.dumps(ret, ensure_ascii=False)

    def download(self, sid):
        if sid == '':
            StdError.error('歌曲下载出错\t没有正确的歌曲id')
            return None
        # 加入MySQL里面的支持，查找到对应的name
        songName = ConnectMysql.get_song_by_id(self.conn, sid)[1]
        if not os.path.isfile(MUSIC_PATH.format(songName)):
            StdError.info("下载链接：" + self.DownloadAPI.format(sid))
            headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36'}
            r = requests.get(self.DownloadAPI.format(sid), headers=headers,allow_redirects=False)
            src = r.headers['location']
            res = requests.get(src)
            with open(MUSIC_PATH.format(songName), 'wb') as f:
                f.write(res.content)
        return songName

    def play(self, song_name):# TODO 后面可能会加上播放功能
        pass


class ActionManager():
    def __init__(self):
        self.DownloadAPI = 'http://music.163.com/song/media/outer/url?id={}'
        self.conn = ConnectMysql.new_connect()
        self.SongURL = 'http://music.163.com'

    def __del__(self):
        self.conn.close()

    def get_action(self, uid, sid):
        data = ConnectMysql.get_actions(self.conn, uid, sid)
        if data == None:
            return json.dumps((0, 0, 0, 0))
        else:
            return json.dumps(data, ensure_ascii=False)

    def set_action(self, uid, sid, like, unlike, audition, download):
        ret = ConnectMysql.set_action(self.conn, uid, sid, like, unlike, audition, download)
        if ret:
            rate = Rate()
            rate.score(uid, sid, like, unlike, audition, download)
        return ret
