from flask import Flask, render_template, make_response, Blueprint, redirect, url_for, abort, request, Response, jsonify, send_from_directory, send_file
from Src.App.models import *
from Src.App.ext import import_cookie, StdError
from Src.App.settings import FILEEXT, PAGE_OFFSET
import mimetypes
import os
import json

# music_recommend_blueprint
blue = Blueprint('MRB', __name__)
# 推荐模块
recommend = MusicRecommend()


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
        if um.register(userName, userPwd, userSUPER, userEmail, userLikes):
            return redirect(url_for('MRB.index'))
        else:
            abort(Response('用户注册失败'))


@blue.route('/forgetpwd/', methods=["GET", "POST"])
def forgetpwd():
    if request.method == "GET":
        return render_template('forgetpwd.html')
    elif request.method == "POST":
        userName = request.form.get('username')
        userNewPwd = request.form.get('userpwd')
        userEmail = request.form.get('useremail')
        um = UserManager()
        if um.forget_passwd(userName, userEmail, userNewPwd):
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

@blue.route('/logout/')
def logout():
    response = make_response(redirect(url_for('MRB.index')))
    cookies = dict(request.cookies)
    for i in cookies.keys():
        response.delete_cookie(i)
    return response

@blue.route('/home/', methods=["GET", "POST"])
def home():
    if request.method == "GET":
        userID = request.cookies.get('user_id')
        userName = request.cookies.get('user_name')
        if userID != None and userName != None:
            return render_template('home.html')
        else:
            return redirect(url_for("MRB.login"))
    elif request.method == "POST":
        songList = request.files.get('uploadlist')
        music = request.files.get('uploadmusic')
        um = UploadMusic()
        ret = True
        res = ""
        if songList != None and os.path.splitext(songList.filename)[-1][1:] in FILEEXT:
            while True:
                try:
                    line = songList.readline()
                    if line == b'':
                        break
                    data = json.loads(line)
                    data = UploadMusic.handle_json(data)
                    ret &= um.upload_list(data)
                    if ret:
                        res += 'list_id={}已导入\n'.format(data['list_id'])
                    else:
                        res += 'list_id={}未成功导入\n'.format(data['list_id'])
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
        if music != None and os.path.splitext(music.filename)[-1][1:] in FILEEXT:
            while True:
                try:
                    line = music.readline()
                    if line == b'':
                        break
                    data = json.loads(line)
                    data = UploadMusic.handle_json(data)
                    ret &= um.upload_music(data)
                    if ret:
                        res += 'song_id={}已导入\n'.format(data['song_id'])
                    else:
                        res += 'song_id={}未成功导入\n'.format(data['song_id'])
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
        if ret:
            return "文件上传成功，已经导入MySQL数据库中\n" + res
        else:
            return "文件上传失败"


@blue.route('/music/', methods=["GET"])
def music():
    return render_template('music.html')


@blue.route('/music/download/', methods=["GET"])
def download():
    sid = int(request.args.get('sid'))
    mm = MusicManager()
    songName = mm.download(sid)
    if songName != None:
        fileName = '{}.mp3'.format(songName)
        with open(MUSIC_PATH.format(songName), 'rb') as f:
            content = f.read()
        response = make_response(content)
        mime_type = mimetypes.guess_type(MUSIC_PATH.format(songName))[0]
        response.headers['Content-Type'] = mime_type
        response.headers['Content-Disposition'] = 'attachment; filename={}'.format(fileName.encode().decode('latin-1'))
        return response
    else:
        abort(Response('歌曲下载失败'))

@blue.route('/search/')
def search():
    return render_template('search.html')


@blue.route('/api/getmusicbase/')
def getmusicbase():
    offset = int(request.args.get('offset') or 0)
    limit = int(request.args.get('limit') or 35)
    uid = int(request.args.get('uid'))
    mm = MusicManager(recommend)
    ret = mm.get_recommend(uid, offset, limit)
    return ret


@blue.route('/api/getlikes/')
def getlikes():
    likes = ConnectMysql.get_likes(ConnectMysql.new_connect())
    return json.dumps(list(likes), ensure_ascii=False)


@blue.route('/api/getsearch/')
def getsearch():
    s = request.args.get('s')
    if len(s) == 1:
        s = s[0]
    elif len(s) > 1:
        s = '%'.join(s)
    else:
        abort(Response("请输入正确的查询字符"))
    ms = MusicSearch()
    return ms.get_music_by_text(s)


@blue.route('/api/issuper/')
def issuper():
    userID = int(request.args.get('uid'))
    um = UserManager()
    ret = um.is_super(userID)
    return jsonify({'isSuper': ret})


@blue.route('/api/getmusicinfo/')
def getmusicinfo():
    songID = int(request.args.get('sid'))
    mm = MusicManager()
    return mm.get_music_info(songID)


@blue.route('/api/getaction/')
def getaction():
    userID = int(request.args.get('uid'))
    songID = int(request.args.get('sid'))
    am = ActionManager()
    return am.get_action(userID, songID)


@blue.route('/api/setaction/', methods=["POST"])
def setaction():
    userID = int(request.args.get('uid'))
    songID = int(request.args.get('sid'))
    like = int(request.form.get('like'))
    unlike = int(request.form.get('unlike'))
    audition = int(request.form.get('audition'))
    download = int(request.form.get('download'))
    am = ActionManager()
    if am.set_action(userID, songID, like, unlike, audition, download):
        return jsonify({"ok": True})
    else:
        return jsonify({"ok": False})

@blue.route('/api/getmusicnum/')
def getmusicnum():
    mm = MusicManager()
    return mm.get_music_num()

@blue.route('/allmusic/')
def allmusic():
    resp = make_response(render_template('allmusic.html'))
    import_cookie(resp, {'curpage': 1})
    return resp

@blue.route('/api/getallmusic/')
def getallmusic():
    page = int(request.args.get('page'))
    offset = request.args.get('offset')
    if offset != None:
        offset = int(offset)
    else:
        offset = PAGE_OFFSET
    mm = MusicManager()
    return mm.get_all_music(page, offset)
