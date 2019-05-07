var b_search = document.getElementById('b-search');
b_search.onclick = function () {
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
                // 这里最好加上分页 TODO
                var songName = json['data'][i][0];
                var songArtist = json['data'][i][1];
                var tr = document.createElement('tr');
                var td1 = document.createElement('td');
                var td1_a = document.createElement('a');
                td1_a.href = '/music?sid=' + json['data'][i][2];
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