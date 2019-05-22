function getCheckBox(name, value) {
    var div = document.createElement('div');
    div.setAttribute('class', "checkbox ");
    // 这个label必须创建，为了bootstrap
    var label = document.createElement('label');
    var inp = document.createElement('input');
    inp.setAttribute("type", "checkbox");
    inp.setAttribute("name", name);
    inp.setAttribute("class", 'form-control');
    inp.setAttribute("value", value);
    var text = document.createTextNode(value);
    label.appendChild(inp);
    label.appendChild(text);
    div.appendChild(label);
    return div;
}

// 获取到标签加入到选择项里面
var ul = document.getElementById('likes');
ajax_get("/api/getlikes/", function (data) {
    var tmp = JSON.parse(data);
    for (var i = 0; i < tmp.length; i++){
        var li = document.createElement('li');
        var che = getCheckBox("userlikes", tmp[i]);
        li.appendChild(che);
        ul.appendChild(li);
    }
})