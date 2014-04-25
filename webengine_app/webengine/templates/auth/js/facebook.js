window.app_id = '{{FACEBOOK_APP_ID}}';
window.is_fb_loggedin = false;
window.fbAsyncInit = function () {
    FB.init({
        appId: '{{FACEBOOK_APP_ID}}',
        status: false, // check login status
        cookie: false, // enable cookies to allow the server to access the session
        xfbml: true,  // parse XFBML
        frictionlessRequests: true
    });
    FB.getLoginStatus(function (response) {
        if (response.status === 'connected') {
            window.is_fb_loggedin = true;
        }
    });
    window.FB = FB;

    window.FB.shareBase64Photo = function (imageData, msg, callback) {
        var mimeType = "image/jpeg";
        try {
            var blob = dataURItoBlob(imageData, mimeType);
        } catch (e) {
            console.log(e);
        }
        var fd = new FormData();
        var accessToken = FB.getAuthResponse()['accessToken'];
        fd.append("access_token", accessToken);
        fd.append("source", blob);
        fd.append("message", msg);

        var xhr = new XMLHttpRequest();
        xhr.open('POST', 'https://graph.facebook.com/me/photos?access_token=' + accessToken, true);
        xhr.onload = xhr.onerror = function () {
            if(callback){
                callback(xhr.responseText);
            }
        };
        xhr.send(fd);
    };

    window.facebook_scope = '{{FACEBOOK_SCOPE}}'
};
(function (d, s, id) {
    var js, fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) {
        return;
    }
    js = d.createElement(s);
    js.id = id;
    js.src = "//connect.facebook.net/en_US/all.js";
    fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));

function dataURItoBlob(dataURI,mime) {
    var byteString = window.atob(dataURI);
    var ia = new Uint8Array(byteString.length);

    for (var i = 0; i < byteString.length; i++) {
        ia[i] = byteString.charCodeAt(i);
    }
    try {
        return new Blob([ia], {type: mime});
    } catch (e) {
        var BlobBuilder = window.WebKitBlobBuilder || window.MozBlobBuilder;
        var bb = new BlobBuilder();
        bb.append(ia);
        return bb.getBlob(mime);
    }
}