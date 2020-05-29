

function publishtesthandle() {
    //window.alert("111");
    //console.debug("123")
    var csrftoken = getCookie('csrftoken');

    $.ajax({
        url: '/android/pushlishtest',
        type: 'post',
        //data: data,
        //dataType: 'json',
        //headers: {'action': 'softwareupgrade'},
        headers: {'X-CSRFToken': csrftoken},
        success: function (response) {
            if (response.code == '0') {
                // swsw
                location.href = response.data.to_url
            } else {
                window.alert("请求测试发布版本页面失败");
            }
        }
    });

}


function versionpublishhandle() {
    var csrftoken = getCookie('csrftoken');

    $.ajax({
        url: '/android/publishversion',
        type: 'post',
        //data: data,
        //dataType: 'json',
        //headers: {'action': 'softwareupgrade'},
        headers: {'X-CSRFToken': csrftoken},
        success: function (response) {
            if (response.code == '0') {
                location.href = response.data.to_url
            } else {
                window.alert("请求正式发布版本页面失败");
            }
        }
    });

}


function versionmanagehandle() {

    var csrftoken = getCookie('csrftoken');

    $.ajax({
        url: '/android/managerversion',
        type: 'post',
        //data: data,
        //dataType: 'json',
        //headers: {'action': 'softwareupgrade'},
        headers: {'X-CSRFToken': csrftoken},
        success: function (response) {
            if (response.code == '0') {
                // swsw
                location.href = response.data.to_url
            } else {
                window.alert("请求版本管理页面失败");
            }
        }
    });

}