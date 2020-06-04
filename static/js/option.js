

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



$(document).ready(function(){
    $("#publishbuttest").click(function(){
        // 阻止form表单自己的提交事件
        event.preventDefault();

        if(window.confirm("发布测试版本,请点击确认")){
        } else {
            return;
        }

        var devicetype = $('#devicetype').val();
        if (!devicetype) {
            $("#error-msg p").html("设备型号不能为空！");
            $("#error-msg p").show();
            return;
        }

        var versionnum = $('#versionnum').val();
        if (!versionnum) {
            $("#error-msg p").html("版本号不能为空！");
            $("#error-msg p").show();
            return;
        }

        var packetmd5value = $('#packetmd5value').val();
        if (!versionnum) {
            $("#error-msg p").html("软件包MD5不能为空！");
            $("#error-msg p").show();
            return;
        }

        var illustrate = $('#illustrate').val();

        var filename = $('#fileupload').val();
        if (!filename) {
            $("#error-msg p").html("未选择发布的升级软件包");
            $("#error-msg p").show();
            return;
        }
        //console.debug(filename);

        $("#error-msg p").hide();

        var csrftoken = getCookie('csrftoken');
        var data = {
            'device': devicetype,
            'version': versionnum,
            'md5': packetmd5value,
            'content': illustrate,
            'filename': filename
        };

        var form = new FormData();

        var fileobj = document.getElementById('fileupload').files[0];
        form.append('packet',fileobj);
        form.append('type',"test");
        form.append('device',devicetype);
        form.append('version',versionnum);
        form.append('md5',packetmd5value);
        form.append('content',illustrate);
        form.append('filename',filename);

        var xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function () {
            if(xhr.readyState == 4){
                var data = xhr.responseText;
                var jsonobj = JSON.parse(data);
                console.log(jsonobj.returncode);
                console.log(jsonobj.msg);
                if(jsonobj.returncode == "0"){
                    alert("发布版本成功!!!!");
                    location.href = jsonobj.to_url
                }else {
                    alert(jsonobj.msg);
                    $("#error-msg p").html(jsonobj.msg);
                    $("#error-msg p").show();
                }
            }
        };
        xhr.open('post','/android/upgradepackage', true);
        xhr.setRequestHeader("X-CSRFToken",csrftoken);
        xhr.upload.onprogress = progressFunction;
        // $("#error-msg p").html("正在上传软件包,请等候");
        // $("#error-msg p").show();
        xhr.send(form);

    });
});


function progressFunction(evt) {
    // evt.total是需要传输的总字节，evt.loaded是已经传输的字节。如果evt.lengthComputable不为真，则evt.total等于0
    if (evt.lengthComputable) {
        var mesg = "正在上传软件包,请等候...";
        mesg += '当前上传进度:'+ Math.round(evt.loaded / evt.total * 100) + "%";
        $("#error-msg p").html(mesg);
        $("#error-msg p").show();
        //console.log('当前上传进度'+ Math.round(evt.loaded / evt.total * 100) + "%");
    }
}


$(document).ready(function(){
    $("#publishbut").click(function(){
        // 阻止form表单自己的提交事件
        event.preventDefault();

        if(window.confirm("发布测试版本,请点击确认")){
        } else {
            return;
        }

        var devicetype = $('#devicetype').val();
        if (!devicetype) {
            $("#error-msg p").html("设备型号不能为空！");
            $("#error-msg p").show();
            return;
        }

        var versionnum = $('#versionnum').val();
        if (!versionnum) {
            $("#error-msg p").html("版本号不能为空！");
            $("#error-msg p").show();
            return;
        }

        var packetmd5value = $('#packetmd5value').val();
        if (!versionnum) {
            $("#error-msg p").html("软件包MD5不能为空！");
            $("#error-msg p").show();
            return;
        }

        var illustrate = $('#illustrate').val();

        var filename = $('#fileupload').val();
        if (!filename) {
            $("#error-msg p").html("未选择发布的升级软件包");
            $("#error-msg p").show();
            return;
        }
        //console.debug(filename);

        $("#error-msg p").hide();

        var csrftoken = getCookie('csrftoken');
        var data = {
            'device': devicetype,
            'version': versionnum,
            'md5': packetmd5value,
            'content': illustrate,
            'filename': filename
        };

        var form = new FormData();

        var fileobj = document.getElementById('fileupload').files[0];
        form.append('packet',fileobj);
        form.append('type',"official");
        form.append('device',devicetype);
        form.append('version',versionnum);
        form.append('md5',packetmd5value);
        form.append('content',illustrate);
        form.append('filename',filename);

        var xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function () {
            if(xhr.readyState == 4){
                var data = xhr.responseText;
                var jsonobj = JSON.parse(data);
                console.log(jsonobj.returncode);
                console.log(jsonobj.msg);
                if(jsonobj.returncode == "0"){
                    alert("发布版本成功!!!!");
                    location.href = jsonobj.to_url
                }else {
                    alert(jsonobj.msg);
                    $("#error-msg p").html(jsonobj.msg);
                    $("#error-msg p").show();
                }
            }
        };
        xhr.open('post','/android/upgradepackage', true);
        xhr.setRequestHeader("X-CSRFToken",csrftoken);
        xhr.upload.onprogress = progressFunction;
        // $("#error-msg p").html("正在上传软件包,请等候");
        // $("#error-msg p").show();
        xhr.send(form);

    });
});




function publishnewspost() {
    $.ajax({
        url: '/android/publishnewstest',
        type: 'post',
        data: data,
        dataType: 'json',
        headers: {'X-CSRFToken': csrftoken},
        success: function (response) {
            if (response.code == '0') {
                window.alert("发布版本成功");
                location.href = response.data.to_url
            } else {
                window.alert("发布版本失败,请从新发布");
            }
        }
    });
}