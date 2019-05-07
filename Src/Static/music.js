function get_action(songid, userid) {
    ajax_get("/api/getaction/?uid=" + userid + "&sid=" + songid, function (data) {
        data = JSON.parse(data);
        data = data[0];
        /*
        * audition     download 
        * liketrue     likefalse 
        * unliketrue     unlikefalse 
        */
        var ilike = document.getElementById('inp-like');
        var like = document.getElementById("like");
        if (data[0] === 0) {
            like.innerText = "喜欢";
        } else if (data[0] === 1) {
            like.innerText = "喜欢";
        }
        ilike.value = String(data[0]);
        var iunlike = document.getElementById('inp-unlike');
        var unlike = document.getElementById("unlike");
        if (data[1] === 0) {
            unlike.innerText = "不感兴趣";
        } else if (data[1] === 1) {
            unlike.innerText = "不感兴趣";
        }
        iunlike.value = String(data[1]);
        var iaudition = document.getElementById('inp-audition');
        iaudition.value = String(data[2]);
        var idownload = document.getElementById('inp-download');
        idownload.value = String(data[3]);
    }, false);
}

function fill_in_music_info(songid) {
    ajax_get("/api/getmusicinfo/?sid=" + songid, function (data) {
        data = JSON.parse(data);
        data = data[0];
        var d_info = document.getElementById('info');
        var f_lyric = document.getElementById('lyric');
        f_lyric.innerHTML = f_lyric.innerHTML.split("\n")[1];
        // 歌曲名称
        if (data[0] != null) {
            var h_name = document.createElement('h3');
            h_name.innerText = data[0];
            d_info.insertBefore(h_name, f_lyric);
        }
        // 歌手名
        if (data[1] != null) {
            var h_artist = document.createElement('h4');
            h_artist.innerText = data[1];
            d_info.insertBefore(h_artist, f_lyric);
        }
        // 歌曲专辑
        if (data[2] != null) {
            var h_album = document.createElement('h5');
            h_album.innerText = data[2];
            d_info.insertBefore(h_album, f_lyric);
        }
        // 歌曲专辑图
        if (data[4] != null) {
            var d_picture = document.createElement('div');
            data[4] = data[4].replace(/\'/g, "\"");
            var picturelist = JSON.parse(data[4]);
            for (var i = 0; i < picturelist.length; i++){
                var img_albumPicture = document.createElement('img');
                img_albumPicture.src = picturelist[i];
                img_albumPicture.setAttribute("width", "400px");
                d_picture.appendChild(img_albumPicture);
            }
            d_info.insertBefore(d_picture, f_lyric);
        }
        // 歌词
        if (data[3] != null) {
            var lyriclist = data[3].split("\n");
            for (var i = 0; i < lyriclist.length; i++) {
                var p_lyric = document.createElement('p');
                p_lyric.innerText = lyriclist[i];
                f_lyric.appendChild(p_lyric);
            }
        }
        // 标签
        if (data[5] != null) {
            var taglist = data[5].split(',');
            var d_tags = document.createElement('div');
            for (var i = 0; i < taglist.length; i++) {
                var span_tag = document.createElement('span');
                span_tag.innerText = taglist[i];
                d_tags.appendChild(span_tag);
            }
            d_info.appendChild(d_tags);
        }
        // 试听链接
        if (data[6] != null) {
            var audition = document.getElementById('a-audition');
            audition.href += data[6];
        }
        // 下载链接
        var download = document.getElementById('a-download');
        download.href += '?sid=' + songid;
    })
}

function on_action(actionName, sid) {
    var ilike = document.getElementById('inp-like');
    var iunlike = document.getElementById('inp-unlike');
    var iaudition = document.getElementById('inp-audition');
    var idownload = document.getElementById('inp-download');
    var action = {
        "like": ilike.value,
        "unlike": iunlike.value,
        "audition": iaudition.value,
        "download": idownload.value
    };
    if (actionName === "like" || actionName === "unlike") {
        action[actionName] = String(action[actionName] ^ 1);
    } else {
        action[actionName] = String(1);
    }
    var uid = getCookie("user_id");
    ajax_post("/api/setaction/?sid=" + sid + "&uid=" + uid, action, false, function (data) {
        data = JSON.parse(data);
        if (data['ok']) {
            get_action(sid, uid);
        }
    });
}

// 填充音乐信息
fill_in_music_info(getUrlArgs("sid"));

// 填充用户曾经的行为信息
get_action(getUrlArgs("sid"), getCookie("user_id"));
// 对用户行为的控件添加对应的事件

var like = document.getElementById("like");
like.onclick = function () {
    var sid = getUrlArgs("sid");
    on_action('like', sid);
};
var unlike = document.getElementById("unlike");
unlike.onclick = function () {
    var sid = getUrlArgs("sid");
    on_action('unlike', sid);
};
var audition = document.getElementById("audition");
audition.onclick = function () {
    var sid = getUrlArgs("sid");
    on_action('audition', sid);
};
var download = document.getElementById("download");
download.onclick = function () {
    var sid = getUrlArgs("sid");
    on_action('download', sid);
};