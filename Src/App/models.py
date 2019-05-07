# 用户管理模块
from Src.App.ext import StdError, ConnectMysql
from Src.App.settings import SCRAPY_PATH, MUSIC_PATH, RATE_PATH, CHROMEDRIVER_PATH, SCORE
import re
import requests
import time
import pymysql
import os
import json
import hashlib
import sys


# 用户管理模块所用到的错误类
class UserManagerError(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


# 用户管理模块
class UserManager(object):
    def __init__(self):
        self.conn = ConnectMysql.new_connect()
        self.superpwd = 'cdq'

    def __del__(self):
        self.conn.close()

    @staticmethod
    def is_super(userID):
        ret = 0
        conn = ConnectMysql.new_connect()
        cursor = conn.cursor()
        try:
            sql = 'select user_SUPER from t_users where user_id={}'.format(userID)
            if cursor.execute(sql) == 1:
                ret = cursor.fetchall()[0][0]
            else:
                raise UserManagerError('未使用正确的userID')
        except UserManagerError as e:
            StdError.error(e.message + "\tuser_id=" + str(userID))
            ret = 0
        except:
            ret = 0
        finally:
            cursor.close()
            conn.close()
            return ret

    @staticmethod
    def get_likes():
        conn = ConnectMysql.new_connect()
        cursor = conn.cursor()
        cursor.execute('select list_tags from t_lists;')
        likes = set()
        datas = cursor.fetchall()
        for data in datas:
            likes.update((json.loads(data[0].replace("'", '"'))))
        cursor.close()
        conn.close
        return json.dumps(list(likes), ensure_ascii=False)

    def register(self, userName, userPwd, userSUPER, userEmail, userLikes=[]):
        ret = 0
        # 创建用户信息
        userPwd = userPwd.encode('utf-8')
        userPwd = hashlib.md5(userPwd).hexdigest()
        # 验证管理员密钥
        if userSUPER == self.superpwd:
            userSUPER = '1'
        else:
            userSUPER = '0'
        cursor = self.conn.cursor()
        try:
            if cursor.execute('select user_id from t_users where user_name=\'{}\';'.format(userName)) != 0:
                raise UserManagerError('已存在相同的用户名')
            sql = 'insert into t_users (user_name, user_SUPER, user_like, user_pwd, user_email) values (\'{}\', {}, \'{}\', \'{}\', \'{}\');'.format(
                userName, userSUPER, ','.join(userLikes), userPwd, userEmail)
            StdError.info("注册用户" + sql)
            cursor.execute(sql)
            self.conn.commit()
        except UserManagerError as e:
            self.conn.rollback()
            StdError.error(e.message + "\tuser_name=" + userName +
                            "\tuser_SUPER=" + str(userSUPER) + "\tuser_pwd=" + str(userPwd))
            ret = -1
        except:
            self.conn.rollback()
            ret = -1
        finally:
            print(ret)
            cursor.close()
            return ret

    def login(self, userName, userPwd):
        cursor = self.conn.cursor()
        userPwd = hashlib.md5(userPwd.encode()).hexdigest()
        try:
            if cursor.execute('select user_id,user_pwd from t_users where user_name=\'{}\' limit 1;'.format(userName)) != 0:
                data = cursor.fetchall()
                if data[0][1] == userPwd:
                    cookie = {'user_id': data[0][0], 'user_name': userName}
                    return cookie
                else:
                    raise UserManagerError('user_name={}, userPwd={}, wrong password!'.format(userName, userPwd))
            else:
                raise UserManagerError('have no this user name!')
        except UserManagerError as e:
            StdError.error(e.message + "\tuser_name=" + userName)
            return None
        finally:
            cursor.close()

    def get_back(self, userName, userEmail, userNewPwd):
        ret = 0
        cursor = self.conn.cursor()
        userNewPwd = hashlib.md5(userNewPwd.encode()).hexdigest()
        try:
            if cursor.execute('select user_id from t_users where user_name=\'{}\' and user_email=\'{}\';'.format(userName, userEmail)) == 0:
                raise UserManagerError('修改密码却没有正确的用户名或用户邮箱')
            userID = cursor.fetchall()[0][0]
            sql = 'update t_users set user_pwd=\'{}\' where user_id={};'.format(
                userNewPwd, userID)
            cursor.execute(sql)
            self.conn.commit()
        except UserManagerError as e:
            self.conn.rollback()
            StdError.error(e.message + "\tuser_name=" + userName + "\tuser_pwd=" + userNewPwd)
            ret = -1
        except:
            self.conn.rollback()
            ret = -1
        finally:
            cursor.close()
            return ret


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
        sql = 'insert into t_lists ({}) values ({}) ON DUPLICATE KEY UPDATE list_id={}'
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
        sql = sql.format(keys, vals, data['list_id'])
        sql = sql.replace("\n", r'\n') + ';'
        sql = sql.replace("\t", r'\t')
        cursor = self.conn.cursor()
        cursor.execute(sql)
        self.conn.commit()
        cursor.close()

    def upload_song(self, data):
        # 将歌单的标签加入到歌曲的属性当中
        sql = 'select list_tags,list_songs from t_lists where list_songs like \'%{}%\';'.format(
            data['song_id'])
        cursor = self.conn.cursor()
        if cursor.execute(sql) != 0:
            song_tags = ''
            ret = cursor.fetchall()
            for i in ret:
                song_tags += ','.join(json.loads(i[0].replace('\'', '"')))
            data['song_tags'] = song_tags
        sql = 'insert into t_songs({}) values({}) ON DUPLICATE KEY UPDATE song_id={}'
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
        sql = sql.format(keys, vals, data['song_id'])
        sql = sql.replace("\n", r'\n') + ';'
        sql = sql.replace("\t", r'\t')
        cursor.execute(sql)
        self.conn.commit()
        cursor.close()

    def __upload_file(self, filepath):
        fp = open(filepath, 'r', encoding='utf-8')
        while True:
            line = fp.readline()[:-2]
            if line == '':
                break
            try:
                data = json.loads(line, encoding='utf-8')
                # 对scrapy爬出来文件有些错误进行处理
                data = UploadMusic.handle_json(data)
                # 对list和song进行单独的处理
                if 'list_id' in data.keys():
                    self.upload_list(data)
                    StdError.info('list_id=%s已导入' % data['list_id'])
                elif 'song_id' in data.keys():
                    self.upload_song(data)
                    StdError.info('song_id=%s已导入' % data['song_id'])
                else:
                    StdError.warn("data缺乏必要的id")
            except FileNotFoundError:
                self.conn.rollback()
                StdError.error('文件不存在，请调用scrapy爬虫创建数据文件')
            except UnicodeDecodeError:
                self.conn.rollback()
                StdError.error('文件格式不能正常解析，请调用scrapy爬虫创建数据文件')
            except json.decoder.JSONDecodeError:
                self.conn.rollback()
                StdError.error('json文件不能解析，需要创建符合格式的json文件（参照Data文件夹下的json）')
            except pymysql.err.IntegrityError:
                self.conn.rollback()
                StdError.error('数据库中已存在这个歌曲')
            except Exception:
                self.conn.rollback()
                StdError.error('未知错误！请联系开发人员\terror line:' + line)

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
            # f.write(str(uid) + "\t" + str(sid) + "\t" + str() + "\t" + str( + ))
            f.write("{}\t{}\t{}\t{}\n".format(uid, sid, score, time.time()))
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
        cursor = self.conn.cursor()
        sql = 'select user_like from t_users where user_id={} limit 1;'.format(uid)
        cursor.execute(sql)
        userLike = cursor.fetchall()[0][0]
        sql = 'select song_tags from t_songs where song_id={} limit 1;'.format(sid)
        cursor.execute(sql)
        songTags = cursor.fetchall()[0][0]
        cursor.close()
        if userLike == None:
            return 0
        elif songTags == None:
            return 0
        else:
            userLike = userLike.split(',')
            uLikeSet = set()
            for i in userLike:
                uLikeSet.add(i)
            songTags = songTags.split(',')
            sLikeSet = set()
            for i in songTags:
                sLikeSet.add(i)
            print(sLikeSet.issubset(uLikeSet))
            print(userLike, songTags)
            print(sLikeSet, uLikeSet)
            if sLikeSet.issubset(uLikeSet):
                return 2
            else:
                return -2

    def __score_comment(self, sid):
        cursor = self.conn.cursor()
        sql = 'select song_comment from t_songs where song_id={};'.format(sid)
        cursor.execute(sql)
        comment = cursor.fetchall()[0][0]
        return comment / SCORE['comment_base'] * SCORE['comments']

    def score(self, uid, sid, like, unlike, audition, download):
        sAction = self.__score_action(like, unlike, audition, download)
        sSimilar = self.__score_similar(uid, sid)
        sComment = self.__score_comment(sid)
        score = sAction + sSimilar + sComment
        StdError.info("行为得分={}\t标签得分={}\t热度得分={}\t最终得分={}".format(sAction, sSimilar, sComment, score))
        self.dump2file(uid, sid, score)


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
        cursor = self.conn.cursor()
        nameSQL = 'select song_name,song_artist,song_id from t_songs where song_name like \'%{}%\' or song_artist like \'%{}%\''.format(text, text)
        res = cursor.execute(nameSQL)
        if res == 0:
            return json.dumps({'num': res})
        else:
            data = cursor.fetchall()
            return json.dumps({'num': res, 'data': data})


# 音乐管理模块
class MusicManager():
    def __init__(self):
        self.DownloadAPI = 'http://music.163.com/song/media/outer/url?id={}'
        self.conn = ConnectMysql.new_connect()
        self.SongURL = 'http://music.163.com'

    def __del__(self):
        self.conn.close()

    def get_recommend(self, offset=0, limit=35):
        cursor = self.conn.cursor()
        # TODO 这里直接从数据库拿的数据，要改成推荐的
        sql = 'select song_name,song_artist,song_id from t_songs limit {},{};'.format(offset, limit)
        cursor.execute(sql)
        data = cursor.fetchall()
        data = json.dumps(list(data), ensure_ascii=False)
        return data

    def get_music_info(self, songid):
        cursor = self.conn.cursor()
        sql = 'select song_name,song_artist,song_album,song_lyric,song_albumPicture,song_tags,song_link from t_songs where song_id={} limit 1;'.format(songid)
        cursor.execute(sql)
        data = cursor.fetchall()
        data = json.dumps(list(data), ensure_ascii=False)
        return data

    # 暂时不会使用这个功能
    # def audition(self, song_id):
    #     from selenium import webdriver
    #     from selenium.webdriver.chrome.options import Options
    #     # chrome 无头版设置
    #     options = Options()
    #     options.add_argument('--no-sandbox')
    #     options.add_argument('--ignore-certificate-errors')
    #     driver = webdriver.Chrome(
    #         executable_path=CHROMEDRIVER_PATH, chrome_options=options)
    #     cursor = self.conn.cursor()
    #     cursor.execute(
    #         'select song_link from t_songs where song_id=' + str(song_id))
    #     data = cursor.fetchall()
    #     song_link = data[0][0]
    #     driver.get(self.SongURL + song_link)

    def download(self, songid):
        if songid == '':
            StdError.error('没有正确的歌曲id')
            return
        # 加入MySQL里面的支持，查找到对应的name
        cursor = self.conn.cursor()
        cursor.execute('select song_name from t_songs where song_id={};'.format(songid))
        data = cursor.fetchall()
        songName = data[0][0]

        if not os.path.isfile(MUSIC_PATH.format(songName)):
            StdError.info("下载链接：" + self.DownloadAPI.format(songid))
            headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36'}
            r = requests.get(self.DownloadAPI.format(songid), headers=headers,allow_redirects=False)
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

    def get_action(self, userid, songid):
        cursor = self.conn.cursor()
        sql = 'select action_like,action_unlike,action_audition,action_download from t_actions where action_user={} and action_song={}'.format(userid, songid)
        if 0 == cursor.execute(sql):
            return json.dumps(((0, 0, 0, 0),))
        else:
            data = cursor.fetchall()
            return json.dumps(data, ensure_ascii=False)

    def set_action(self, uid, sid, like, unlike, audition, download):
        ret = True
        cursor = self.conn.cursor()
        sql = 'select action_id from t_actions where action_user={} and action_song={};'.format(uid, sid)
        if cursor.execute(sql) == 0:
            sql = 'insert into t_actions (action_user, action_song, action_like, action_unlike, action_audition, action_download) values ({}, {}, {}, {}, {}, {});'.format(uid, sid, like, unlike, audition, download)
            StdError.info("用户行为新增：uid={},sid={}".format(uid, sid))
        else:
            sql = 'update t_actions set action_like={}, action_unlike={}, action_audition={}, action_download={} where action_user={} and action_song={};'.format(like, unlike, audition, download, uid, sid)
            StdError.info("用户行为更新：uid={},sid={}".format(uid, sid))
        try:
            cursor.execute(sql)
            self.conn.commit()
        except:
            self.conn.rollback()
            StdError.error(sql)
            ret = False
        finally:
            cursor.close()
            rate = Rate()
            rate.score(uid, sid, like, unlike, audition, download)
            return ret
