function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i].trim();
        if (c.indexOf(name) == 0) return c.substring(name.length, c.length);
    }
    return "";
}

function getUrlArgs(key) {
    if (key == "") return null;
    else key = key + "=";
    var url = document.location.href;
    var tmp = url.split('?')[1];
    var args = tmp.split('&');
    for (var i = 0; i < args.length; i++) {
        var j = args[i].trim();
        if (j.indexOf(key) == 0)
            return j.substring(key.length, j.length);
    }
    return "";
}

function ajax_get(url, f_callback, sync) {
    sync = sync || true;
    var ajax = new XMLHttpRequest();
    ajax.open('get', url, sync);
    ajax.send();
    ajax.onreadystatechange = function () {
        if (ajax.readyState == 4 && ajax.status == 200) {
            f_callback(ajax.responseText);
        }
    }
}

function ajax_post(url, data, sync, f_callback) {
    sync = sync || true;
    f_callback = f_callback || console.log;
    xhr = new XMLHttpRequest();
    xhr.open('post', url, sync);
    //设置header
    xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
    var postStr = '';
    for (var key in data) {
        postStr += key + "=" + data[key] + "&";
    };
    postStr = postStr.substring(0, postStr.length - 1);
    xhr.send(postStr);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && (xhr.status === 200 || xhr.status === 304)) {
            f_callback(xhr.responseText);
        }
    }
}