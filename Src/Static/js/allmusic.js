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

// 请求cookie中的当前页
function handle_page(el, val, disable, needChangeText=true) {
    el.dataset['page'] = val;
    if (needChangeText) {
        el.innerText = val;
    }
    if (disable) {
        el.className = "btn btn-default"
    } else {
        el.className = "btn btn-default disabled"
    }
}

var p = document.getElementById('previous');
var cur = document.getElementById('current');
var sec = document.getElementById('second');
var n = document.getElementById('next');
function paging_onclick(btnid) {
    num = this.dataset['page'];
    var help = document.getElementById('help');
    help.style.display = "block";
    ajax_get("/api/getallmusic/" + "?page=" + num, function (json) {
        // 处理分页按钮
        var page = JSON.parse(json)['page'];
        handle_page(cur, page['cur'], false)
        handle_page(p, page['pre'], page['has_pre'], false);
        handle_page(sec, page['sec'], page['has_sec']);
        handle_page(n, page['next'], page['has_next'], false);
        // 添加数据
        var data = JSON.parse(json)['data'];
        var tbody = document.getElementById('sdata');
        var childs = tbody.childNodes;
        while (childs.length != 0) {
            tbody.removeChild(childs[0]);
        }
        var num = data.length;
        for (var i = 0; i < num; i++) {
            var songName = data[i][1];
            var songArtist = data[i][2];
            var tr = document.createElement('tr');
            var td1 = document.createElement('td');
            var td1_a = document.createElement('a');
            td1_a.href = '/music?sid=' + data[i][0];
            td1_a.innerText = songName;
            td1.appendChild(td1_a);
            var td2 = document.createElement('td')
            td2.innerText = songArtist;
            tr.appendChild(td1);
            tr.appendChild(td2);
            tbody.appendChild(tr);
        }
    })
    help.style.display = "none";
}
// 为按钮添加点击事件
p.onclick = paging_onclick;
cur.onclick = paging_onclick;
sec.onclick = paging_onclick;
n.onclick = paging_onclick;
// 为第一页触发事件
cur.onclick();