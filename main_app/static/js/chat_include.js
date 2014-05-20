var scriptPath = script.src;
PATH = scriptPath.split("/")[2]
STATIC_URL = 'http://'+PATH+'/static/'
CHAT_URL = 'http://'+PATH+'/visitor_chat'
REQUEST_URL = 'http://'+PATH+'/visitor_requestchat'
MESSAGE_URL = 'http://'+PATH+'/visitor_message'
CLOSE_URL = 'http://'+PATH+'/visitor_delete'
TYPE_URL = 'http://'+PATH+'/visitor_type'
COOKIE_URL = 'http://'+PATH+'/cookie_check'

function loadScripts(src, callback) {
    var d = document, head = d.getElementsByTagName('head')[0], node = null, i = 0, j = 0, done = false;
    for (i = 0, j = src.length; i < j; i += 1) {
        if (src[i].match(/\.js/i)) {
            node = d.createElement('script');
            node.type = 'text/javascript';
            node.src = src[i];
        } else if (src[i].match(/\.css/i)) {
            node = d.createElement('link');
            node.type = 'text/css';
            node.rel = 'stylesheet';
            node.href = src[i];
        }
        head.appendChild(node);
    }
    node.onload = node.onreadystatechange = function() {
        if (!done && (!this.readyState || this.readyState == "loaded" || this.readyState == "complete")) {
            done = true;
            callback();
        }
    };
}
require_jquery = 'http://ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js'
loadScripts(new Array(require_jquery), function() {
    var scripts = new Array();
    scripts.push("http://js.pusher.com/2.2/pusher.min.js");
    scripts.push(STATIC_URL + 'js/chat.js');
    scripts.push(STATIC_URL + 'js/jquery.cookie.js');
    scripts.push(STATIC_URL + 'plugins/bootstrap/css/bootstrap.css');
    scripts.push(STATIC_URL + 'css/chat.css');
    scripts.push(STATIC_URL + 'css/main.css');
    scripts.push(STATIC_URL + 'css/theme.css');
    scripts.push(STATIC_URL + 'css/MoneAdmin.css');
    loadScripts(scripts, function() {});
});