from Src.App.settings import LOG_PATH, DB_SETTING
import pymysql
import sys
from flask import Response


# 工具类
class ConnectMysql(object):
    @staticmethod
    def new_connect():
        conn = pymysql.connect(host=DB_SETTING['host'], user=DB_SETTING['user'],
                                passwd=DB_SETTING['passwd'], charset=DB_SETTING['charset'], port=DB_SETTING['port'])
        cur = conn.cursor()
        cur.execute(r'set names utf8')
        cur.execute(r'use music_recommend')
        cur.close()
        return conn


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

def import_cookie(resp: Response, cookies: dict):
    for k, v in cookies.items():
        resp.set_cookie(str(k), str(v))
    return resp
