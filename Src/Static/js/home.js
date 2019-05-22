// 在welcome后加上用户名
var userName = getCookie("user_name");
var w = document.getElementById("welcome");
w.innerHTML += ", " + userName;

// 给管理员加上特定服务接口
var field = document.getElementById('super');
var userID = getCookie("user_id");
ajax_get("/api/issuper/" + "?uid=" + userID, function (data) {
    var tmp = JSON.parse(data);
    if (tmp['isSuper']) {
        field.style.display = "block";
    }
})

// 接收json歌曲数据
var t = document.getElementById('t_recommend');
ajax_get("/api/getmusicbase/" + "?uid=" + userID, function (data) {
    var tmp = JSON.parse(data);
    for (var i = 0; i < tmp.length; i++){
        var tr = document.createElement('tr');
        var songID = tmp[i][0];
        var songName = tmp[i][1];
        var songArtist = tmp[i][2];
        var td_name = document.createElement('td');
        var a_name = document.createElement('a');
        a_name.appendChild(document.createTextNode(songName));
        a_name.href = '/music/?sid=' + songID;
        td_name.appendChild(a_name);
        var td_artist = document.createElement('td');
        td_artist.innerHTML = songArtist;

        tr.appendChild(td_name);
        tr.appendChild(td_artist);
        t.appendChild(tr);
    }
})
