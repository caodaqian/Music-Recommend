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

// 搜索歌曲
var table = document.getElementsByTagName('table')[0];
var d_search = document.getElementById('dialog-search');
var b_search = document.getElementById('b-search');
b_search.onclick = function () {
    table.style.display = "table";
    d_search.style.margin = "10% auto";
    var s = document.getElementById('t-search').value;
    var tbody = document.getElementById('sdata');
    var childs = tbody.childNodes;
    while (childs.length != 0) {
        tbody.removeChild(childs[0]);
    }
    ajax_get('/api/getsearch' + "?s=" + s, function (data) {
        var json = JSON.parse(data);
        var num = json['num'];
        if (num != 0) {
            for (var i = 0; i < num; i++){
                var songName = json['data'][i][1];
                var songArtist = json['data'][i][2];
                var tr = document.createElement('tr');
                var td1 = document.createElement('td');
                var td1_a = document.createElement('a');
                td1_a.href = '/music?sid=' + json['data'][i][0];
                td1_a.innerText = songName;
                td1.appendChild(td1_a);
                var td2 = document.createElement('td')
                td2.innerText = songArtist;
                tr.appendChild(td1);
                tr.appendChild(td2);
                tbody.appendChild(tr);
            }
        }
    })
}