from Src.App.settings import LOG_PATH, DB_SETTING
import pymysql
import sys
from flask import Response
import json


# 用户管理模块所用到的错误类
class UserManagerError(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message

    def __str__(self):
        return self.message


# 数据库连接类
class ConnectMysql(object):
    @staticmethod
    def new_connect():
        conn = pymysql.connect(host=DB_SETTING['host'], user=DB_SETTING['user'],
                                passwd=DB_SETTING['passwd'], charset=DB_SETTING['charset'],
                                port=DB_SETTING['port'])
        cur = conn.cursor()
        cur.execute(r'set names utf8')
        cur.execute(r'use music_recommend')
        cur.close()
        return conn

    @staticmethod
    def get_likes(db: pymysql.connections.Connection):
        cursor = db.cursor()
        cursor.execute('select list_tags from t_lists;')
        likes = set()
        datas = cursor.fetchall()
        for data in datas:
            likes.update((json.loads(data[0].replace("'", '"'))))
        cursor.close()
        return likes

    @staticmethod
    def get_actions(db: pymysql.connections.Connection, uid=None, sid=None):
        cursor = db.cursor()
        if uid == None and sid == None:
            sql = 'select * from t_actions;'
            cursor.execute(sql)
            data = cursor.fetchall()
        elif uid == None:
            sql = 'select action_like,action_unlike,action_audition,action_download from t_actions where action_song={};'
            cursor.execute(sql.format(sid))
            data = cursor.fetchall()
        elif sid == None:
            sql = 'select action_like,action_unlike,action_audition,action_download from t_actions where action_user={};'
            cursor.execute(sql.format(uid))
            data = cursor.fetchall()
        else:
            sql = 'select action_like,action_unlike,action_audition,action_download from t_actions where action_user={} and action_song={} limit 1;'
            cursor.execute(sql.format(uid, sid))
            data = cursor.fetchone()
        cursor.close()
        return data

    @staticmethod
    def set_action(db: pymysql.connections.Connection, uid, sid, like, unlike, audition, download):
        ret = False
        cursor = db.cursor()
        sql = 'select action_id from t_actions where action_user={} and action_song={};'.format(uid, sid)
        if cursor.execute(sql) == 0:
            sql = 'insert into t_actions (action_user, action_song, action_like, action_unlike, action_audition, action_download) values ({}, {}, {}, {}, {}, {});'.format(uid, sid, like, unlike, audition, download)
            StdError.info("用户行为新增：uid={},sid={}".format(uid, sid))
        else:
            sql = 'update t_actions set action_like={}, action_unlike={}, action_audition={}, action_download={} where action_user={} and action_song={};'.format(like, unlike, audition, download, uid, sid)
            StdError.info("用户行为更新：uid={},sid={}".format(uid, sid))
        try:
            cursor.execute(sql)
            db.commit()
            ret = True
        except:
            db.rollback()
            StdError.error("行为设置出现未知错误\tuid={},sid={},sql={}".format(uid, sid, sql))
            ret = False
        finally:
            cursor.close()
            return ret

    @staticmethod
    def is_user_super(db: pymysql.connections.Connection, uid):
        ret = 0
        cursor = db.cursor()
        sql = 'select user_SUPER from t_users where user_id={} limit 1;'.format(
            uid)
        try:
            cursor.execute(sql)
            ret = cursor.fetchone()[0]
        except:
            ret = 0
        finally:
            cursor.close()
            return ret

    @staticmethod
    def get_user_tags(db: pymysql.connections.Connection, user):
        cursor = db.cursor()
        if isinstance(user, int):
            sql = "select user_like from t_users where user_id={} limit 1;".format(user)
        else:
            sql = "select user_like from t_users where user_name='{}' limit 1;".format(user)
        cursor.execute(sql)
        data = cursor.fetchone()[0]
        cursor.close()
        if data != None:
            return list(data.split(','))
        else:
            return None

    @staticmethod
    def get_song_tags(db: pymysql.connections.Connection, song):
        cursor = db.cursor()
        if isinstance(song, int):
            sql = "select song_tags from t_songs where song_id={} limit 1;".format(song)
        else:
            sql = "select song_tags from t_songs where song_name='{}' limit 1;".format(song)
        cursor.execute(sql)
        data = cursor.fetchone()[0]
        cursor.close()
        if data != None:
            return list(data.split(','))
        else:
            return None

    @staticmethod
    def get_song_comment(db: pymysql.connections.Connection, song):
        cursor = db.cursor()
        if isinstance(song, int):
            sql = 'select song_comment from t_songs where song_id={} limit 1;'.format(song)
        else:
            sql = "select song_tags from t_songs where song_name='{}' limit 1;".format(song)
        cursor.execute(sql)
        comment = cursor.fetchone()[0]
        cursor.close()
        return comment

    @staticmethod
    def get_song_info(db: pymysql.connections.Connection, song):
        cursor = db.cursor()
        if isinstance(song, int):
            sql = 'select song_name,song_artist,song_album,song_lyric,song_albumPicture,song_tags,song_link from t_songs where song_id={} limit 1;'.format(song)
        else:
            sql = 'select song_name,song_artist,song_album,song_lyric,song_albumPicture,song_tags,song_link from t_songs where song_name=\'{}\' limit 1;'.format(song)
        cursor.execute(sql)
        data = cursor.fetchone()
        cursor.close()
        return data

    @staticmethod
    def get_song_by_id(db: pymysql.connections.Connection, sid):
        cursor = db.cursor()
        sql = 'select song_id,song_name,song_artist from t_songs where song_id={} limit 1;'
        cursor.execute(sql.format(sid))
        data = cursor.fetchone()
        cursor.close()
        return data

    @staticmethod
    def get_songs_by_random(db: pymysql.connections.Connection, need):
        cursor = db.cursor()
        cursor.execute('select song_id,song_name,song_artist from t_songs ORDER BY RAND() LIMIT {};'.format(need))
        data = cursor.fetchall()
        cursor.close()
        return list(data)

    @staticmethod
    def get_songs_by_tags(db: pymysql.connections.Connection, tags: list, limit):
        cursor = db.cursor()
        sql = "select song_id,song_name,song_artist from t_songs where song_tags like '%{}%' limit {};"
        ret = []
        for i in tags:
            limit -= cursor.execute(sql.format(i, limit))
            data = cursor.fetchall()
            ret.extend(list(data))
            if limit <= 0:
                break
        cursor.close()
        return ret

    @staticmethod
    def get_songs_by_search(db: pymysql.connections.Connection, s):
        cursor = db.cursor()
        sql = 'select song_id,song_name,song_artist from t_songs where song_name like \'%{}%\' or song_artist like \'%{}%\''
        res = cursor.execute(sql.format(s, s))
        if res == 0:
            ret = {'num': res}
        else:
            data = cursor.fetchall()
            ret = {
                'num': res,
                'data': data
            }
        cursor.close()
        return ret

    @staticmethod
    def user_register(db: pymysql.connections.Connection, userName, userPwd, userSUPER, userEmail, userLikes):
        cursor = db.cursor()
        ret = False
        try:
            if cursor.execute('select user_id from t_users where user_name=\'{}\';'.format(userName)) != 0:
                raise UserManagerError('用户注册错误，已存在相同的用户名')
            sql = 'insert into t_users (user_name, user_SUPER, user_like, user_pwd, user_email) values (\'{}\', {}, \'{}\', \'{}\', \'{}\');'
            sql = sql.format(userName, userSUPER, ','.join(userLikes), userPwd, userEmail)
            StdError.info("注册用户" + sql)
            cursor.execute(sql)
            db.commit()
            ret = True
        except UserManagerError as e:
            db.rollback()
            StdError.warn(e.message + "\tuser_name=" + userName + "\tuser_SUPER=" + str(userSUPER) + "\tuser_pwd=" + str(userPwd) + "\tuser_email=" + userEmail + "\tuser_likes=" + userLikes)
        except pymysql.err.IntegrityError as e:
            db.rollback()
            StdError.error(str(e) + "\tuser_name=" + userName + "\tuser_SUPER=" + str(userSUPER) + "\tuser_pwd=" + str(userPwd) + "\tuser_email=" + userEmail + "\tuser_likes=" + userLikes)
        except:
            db.rollback()
            StdError.error("用户注册出现未知错误" + "\tuser_name=" + userName + "\tuser_SUPER=" + str(userSUPER) + "\tuser_pwd=" + str(userPwd) + "\tuser_email=" + userEmail + "\tuser_likes=" + userLikes)
        finally:
            cursor.close()
            return ret

    @staticmethod
    def user_login(db: pymysql.connections.Connection, userName, userPwd):
        cursor = db.cursor()
        ret = -1
        try:
            sql = 'select user_id,user_pwd from t_users where user_name=\'{}\' limit 1;'.format(userName)
            if cursor.execute(sql) != 0:
                data = cursor.fetchone()
                if data[1] == userPwd:
                    ret = data[0]
                else:
                    raise UserManagerError("用户登陆错误，用户密码不匹配")
            else:
                raise UserManagerError("用户登陆错误，未找到匹配的注册用户")
        except UserManagerError as e:
            StdError.warn(e.message + "\tuser_name=" + userName + "\tuser_pwd=" + userPwd)
        except:
            StdError.error("用户登录出现未知错误" + "\tuser_name=" + userName + "\tuser_pwd=" + userPwd)
        finally:
            cursor.close()
            return ret

    @staticmethod
    def user_forget_passwd(db: pymysql.connections.Connection, userName, userEmail, userNewPwd):
        cursor = db.cursor()
        ret = False
        try:
            sql = 'select user_id from t_users where user_name=\'{}\' and user_email=\'{}\';'.format(userName, userEmail)
            if cursor.execute(sql) == 0:
                raise UserManagerError("用户修改密码错误，没有找到符合的用户")
            else:
                uid = cursor.fetchone()[0]
                sql = 'update t_users set user_pwd=\'{}\' where user_id={};'.format(userNewPwd, uid)
                cursor.execute(sql)
                db.commit()
                ret = True
        except UserManagerError as e:
            StdError.error(e.message + "\tuser_name=" + userName + "\tuser_pwd=" + userNewPwd + "\tuser_email=" + userEmail)
        except:
            StdError.error("用户修改密码出现未知错误" + "\tuser_name=" + userName + "\tuser_pwd=" + userNewPwd + "\tuser_email=" + userEmail)
        finally:
            cursor.close()
            return ret

    @staticmethod
    def upload_list(db: pymysql.connections.Connection, fields, values, lid):
        ret = False
        cursor = db.cursor()
        sql = 'insert into t_lists ({}) values ({}) ON DUPLICATE KEY UPDATE list_id={};'
        sql = sql.format(fields, values, lid)
        sql = sql.replace("\n", r'\n')
        sql = sql.replace("\t", r'\t')
        try:
            cursor.execute(sql)
            db.commit()
            ret = True
        except:
            StdError.error("上传模块歌单上传出现未知错误\tsql=" + sql)
            db.rollback()
        finally:
            cursor.close()
            return ret

    @staticmethod
    def get_tags_from_list(db: pymysql.connections.Connection, sid):
        cursor = db.cursor()
        sql = 'select list_tags from t_lists where list_songs like \'%{}%\';'.format(sid)
        songTags = ''
        if cursor.execute(sql) != 0:
            data = cursor.fetchall()
            for i in data:
                songTags += ','.join(json.loads(i[0].replace('\'', '"')))
        return songTags

    @staticmethod
    def upload_song(db: pymysql.connections.Connection, fields, values, sid):
        ret = False
        cursor = db.cursor()
        sql = 'insert into t_songs({}) values({}) ON DUPLICATE KEY UPDATE song_id={};'
        sql = sql.format(fields, values, sid)
        try:
            cursor.execute(sql)
            db.commit()
            ret = True
        except:
            StdError.error("上传模块歌曲上传出现未知错误\tsql=" + sql)
            db.rollback()
        finally:
            cursor.close()
            return ret

    @staticmethod
    def get_music_number(db: pymysql.connections.Connection):
        cursor = db.cursor()
        cursor.execute('select count(song_id) from t_songs;')
        data = cursor.fetchone()[0]
        cursor.close()
        return data

    @staticmethod
    def get_all_music(db: pymysql.connections.Connection, start, limit):
        cursor = db.cursor()
        sql = 'select song_id,song_name,song_artist from t_songs limit {},{};'
        cursor.execute(sql.format(start, limit))
        data = cursor.fetchall()
        cursor.close()
        return list(data)


# 错误输出类
class StdError(object):
    @staticmethod
    def info(s, needsavefile=False):
        sys.stderr.write('[info]:' + s + "\n")
        if needsavefile:
            with open(LOG_PATH + "info.log", "a") as f:
                f.write('[info]:' + s + "\n")

    @staticmethod
    def warn(s, needsavefile=False):
        sys.stderr.write('[warn]:' + s + "\n")
        if needsavefile:
            with open(LOG_PATH + "warn.log", "a") as f:
                f.write('[warn]:' + s + "\n")

    @staticmethod
    def error(s, needsavefile=True):
        sys.stderr.write('[err:]' + s + "\n")
        if needsavefile:
            with open(LOG_PATH + "err.log", "a") as f:
                f.write('[err:]' + s + "\n")


# 工具-批量设置cookie
def import_cookie(resp: Response, cookies: dict):
    for k, v in cookies.items():
        resp.set_cookie(str(k), str(v))
    return resp


# 分页器
class Pages():
    def __init__(self):
        self.conn = ConnectMysql.new_connect()
        self.totalPages = -1
        self.currentPage = -1
        self.next = -1
        self.sec = -1
        self.previous = -1
        self.has_next = False
        self.has_pre = False
        self.has_sec = False

    def check_and_ret(self, page, offset):
        self.currentPage = page
        self.sec = page + 1
        self.previous = page - 1
        self.next = page + 2
        number = ConnectMysql.get_music_number(self.conn)
        self.totalPages = number // offset + 1
        if self.currentPage > 1:
            self.has_pre = True
        if self.currentPage < self.totalPages:
            self.has_sec = True
        if self.currentPage + 1 < self.totalPages:
            self.has_next = True
        return self.get_page_info()

    def get_page_info(self):
        data = {
            'total': self.totalPages,
            'next': self.next,
            'pre': self.previous,
            'cur': self.currentPage,
            'sec': self.sec,
            'has_next': self.has_next,
            'has_pre': self.has_pre,
            'has_sec': self.has_sec
        }
        return data
