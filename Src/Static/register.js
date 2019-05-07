function getCheckBox(name) {
    var inp = document.createElement('input');
    inp.setAttribute("type", "checkbox");
    inp.setAttribute("name", name);
    return inp;
}

// 获取到标签加入到选择项里面
var ul = document.getElementById('likes');
ajax_get("/api/getlikes/", function (data) {
    var tmp = JSON.parse(data);
    for (var i = 0; i < tmp.length; i++){
        var li = document.createElement('li');
        var che = getCheckBox("userlikes");
        che.setAttribute("value", tmp[i]);
        var text = document.createTextNode(tmp[i]);
        li.appendChild(che);
        li.appendChild(text);
        ul.appendChild(li);
    }
})