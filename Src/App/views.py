from flask import Flask, render_template, make_response, Blueprint, redirect, url_for, abort, request, Response, jsonify, send_from_directory, send_file
from Src.App.models import *
from Src.App.ext import import_cookie
from Src.App.settings import FILEEXT
import os
import json

# music_recommend_blueprint
blue = Blueprint('MRB', __name__)


@blue.route('/')
def hello():
    return redirect(url_for('MRB.index'), 301)


@blue.route('/favcion.ico')
def favcion():
    return send_from_directory(os.path.join(blue.root_path, 'static'), 'favico.ico', mimetype='image/vnd.microsoft.icon')

@blue.route('/index/')
def index():
    return render_template('index.html')


@blue.route('/register/', methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template('register.html')
    elif request.method == "POST":
        um = UserManager()
        userName = request.form.get('username')
        userPwd = request.form.get('userpwd')
        userEmail = request.form.get('useremail')
        userLikes = request.form.getlist('userlikes')
        userSUPER = request.form.get('userSUPER')
        if 0 == um.register(userName, userPwd, userSUPER, userEmail, userLikes):
            return redirect(url_for('MRB.index'))
        else:
            abort(Response('用户注册失败'))


@blue.route('/getback/', methods=["GET", "POST"])
def getback():
    if request.method == "GET":
        return render_template('getback.html')
    elif request.method == "POST":
        userName = request.form.get('username')
        userNewPwd = request.form.get('userpwd')
        userEmail = request.form.get('useremail')
        um = UserManager()
        if um.get_back(userName, userEmail, userNewPwd) != -1:
            return redirect(url_for('MRB.index'))
        else:
            abort(Response('用户修改密码失败'))


@blue.route('/login/', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template('login.html')
    elif request.method == "POST":
        userName = request.form.get('username')
        userPwd = request.form.get('userpwd')
        um = UserManager()
        cookie = um.login(userName, userPwd)
        if cookie == None:
            abort(Response('用户登陆失败'))
        else:
            resp = make_response(render_template('home.html'))
            import_cookie(resp, cookie)
            return resp


@blue.route('/home/', methods=["POST"])
def home():
    songList = request.files.get('uploadlist')
    music = request.files.get('uploadmusic')
    um = UploadMusic()
    if os.path.splitext(songList.filename)[-1][1:] in FILEEXT:
        while True:
            try:
                line = songList.readline()[:-1]
                if line == b'':
                    break
                data = json.loads(line)
                data = UploadMusic.handle_json(data)
                um.upload_list(data)
            except FileNotFoundError:
                StdError.error('上传歌单文件不存在，请重新上传文件')
                abort(Response("上传歌单文件不存在，请重新上传文件"))
            except UnicodeDecodeError:
                StdError.error('上传的歌单文件格式不能正常解析，需要uft-8编码')
                abort(Response("上传的歌单文件格式不能正常解析，需要uft-8编码"))
            except json.JSONDecodeError:
                StdError.error("上传歌单json解析失效")
                abort(Response("上传歌单json无效，请参照Scrapy爬虫数据进行json的审核"))
            except:
                StdError.error("上传歌单文件遭遇未知错误")
                abort(Response("歌单文件出现未知错误，请参照Scrapy爬虫数据进行json的审核"))
    if os.path.splitext(music.filename)[-1][1:] in FILEEXT:
        while True:
            try:
                line = songList.readline()[:-1]
                if line == b'':
                    break
                data = json.loads(line)
                data = UploadMusic.handle_json(data)
                um.upload_song(data)
            except FileNotFoundError:
                StdError.error('上传歌曲文件不存在，请重新上传文件')
                abort(Response("上传歌曲文件不存在，请重新上传文件"))
            except UnicodeDecodeError:
                StdError.error('上传的歌曲文件格式不能正常解析，需要uft-8编码')
                abort(Response("上传的歌曲文件格式不能正常解析，需要uft-8编码"))
            except json.JSONDecodeError:
                StdError.error("上传歌曲json解析失效")
                abort(Response("上传歌曲json无效，请参照Scrapy爬虫数据进行json的审核"))
            except:
                StdError.error("上传歌曲文件遭遇未知错误")
                abort(Response("歌曲文件出现未知错误，请参照Scrapy爬虫数据进行json的审核"))
    return "文件上传成功，已经导入MySQL数据库中"


@blue.route('/music/', methods=["GET"])
def music():
    # uid = request.args.get('uid')
    return render_template('music.html')


@blue.route('/music/download/', methods=["GET"])
def download():
    sid = request.args.get('sid')
    mm = MusicManager()
    songName = mm.download(sid)
    response = make_response(send_file(MUSIC_PATH.format(songName), as_attachment=True))
    response.headers['Content-Dispostion'] = 'attachment; filname={};'.format(
        songName.encode().decode('latin-1'))
    return response

@blue.route('/search/')
def search():
    return render_template('search.html')


@blue.route('/api/getmusicbase/')
def getmusicbase():
    offset = request.args.get('offset') or 0
    limit = request.args.get('limit') or 35
    mm = MusicManager()
    return mm.get_recommend(offset, limit)


@blue.route('/api/getlikes/')
def getlikes():
    likes = UserManager.get_likes()
    return likes


@blue.route('/api/getsearch/')
def getsearch():
    s = request.args.get('s')
    if len(s) == 1:
        s = s[1]
    elif len(s) > 1:
        s = '%'.join(s)
    else:
        abort(Response("请输入正确的查询字符"))
    ms = MusicSearch()
    return ms.get_music_by_text(s)


@blue.route('/api/issuper/')
def issuper():
    userID = request.args.get('uid')
    ret = UserManager.is_super(userID)
    return jsonify({'isSuper': ret})


@blue.route('/api/getmusicinfo/')
def getmusicinfo():
    songID = request.args.get('sid')
    mm = MusicManager()
    return mm.get_music_info(songID)


@blue.route('/api/getaction/')
def getaction():
    userID = request.args.get('uid')
    songID = request.args.get('sid')
    am = ActionManager()
    return am.get_action(userID, songID)


@blue.route('/api/setaction/', methods=["POST"])
def setaction():
    userID = request.args.get('uid')
    songID = request.args.get('sid')
    like = int(request.form.get('like'))
    unlike = int(request.form.get('unlike'))
    audition = int(request.form.get('audition'))
    download = int(request.form.get('download'))
    am = ActionManager()
    if am.set_action(userID, songID, like, unlike, audition, download):
        return jsonify({"ok": True})
    else:
        return jsonify({"ok": False})
