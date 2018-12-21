var csrftoken = getCookie('csrftoken');

$(window).load(function () {
    isWork();
    if (window.applicationCache) {
            $('#pack_con').uploadifive({
                'auto': true,
                'formData': {
                    'folder': 'pack',
                    'csrfmiddlewaretoken':csrftoken
                },
                'buttonText': '浏  览',
                'queueID': 'queue',
                'uploadScript': '/pack/upload',
                'onUploadComplete': function (file, data) {
                    var json_data = JSON.parse(data);
                    $("#pack_uuid").text(json_data.data.file_uuid_name);       //成功处理file.name
                    $("#MainContent_hiddenpack").val(json_data.data.file_uuid_name);
                }
            });
            $('#md5_con').uploadifive({
                'auto': true,
                'formData': {
                    'folder': 'md5',
                    'csrfmiddlewaretoken':csrftoken
                },
                'uploadLimit': '1',
                'buttonText': '浏  览',
                'queueID': 'queuemd5',
                'uploadScript': 'pack/upload',
                'onUploadComplete': function (file, data) {
                    var json_data = JSON.parse(data);
                    $("#md5_uuid").text(json_data.data.file_uuid_name);       //成功处理file.name
                    $("#MainContent_hiddenmd5").val(json_data.data.file_uuid_name);       //成功处理file.name
                }
            });
    }
    else {
        $('#pack_con').uploadify({
            'formData': {
                'folder': 'pack',
                'csrfmiddlewaretoken':csrftoken
            },
            'buttonText': '浏  览',
            'swf': '/static/js/uploadify.swf',
            'uploader': '/pack/upload',
            'queueSizeLimit': 1,
            'onUploadSuccess': function (file, data, response) {
                var json_data = JSON.parse(data);
                $("#pack_uuid").text(json_data.data.file_uuid_name);       //成功处理file.name
                $("#MainContent_hiddenpack").val(json_data.data.file_uuid_name);
            },
            'onUploadError': function (event, queueId, fileObj, errorObj) {
                alert(errorObj.type + "：" + errorObj.info);
            }
        });
        $('#md5_con').uploadify({
            'formData': {
                'folder': 'md5',
                'csrfmiddlewaretoken':csrftoken
            },
            'buttonText': '浏  览',
            'swf': '/static/js/uploadify.swf',
            'uploader': '/pack/upload',
            // 'onUploadStart': function (file) {
            //    $("#file_upload").uploadify("settings", 'formData', { 'folder': 'md5', 'guid': '' }); //前面两个参数固定，后面第三个为自定义传递的动态传参数
            //  },
            'onUploadSuccess': function (file, data, response) {
                var json_data = JSON.parse(data);
                $("#md5_uuid").text(json_data.data.file_uuid_name);       //成功处理file.name
                $("#MainContent_hiddenmd5").val(json_data.data.file_uuid_name);       //成功处理file.name
            },
            'onUploadError': function (event, queueId, fileObj, errorObj) {
                alert(errorObj.type + "：" + errorObj.info);
            }
        });
    }
});

$(function () {
    $('#pack_info').submit(function (event) {
        // 阻⽌止表单默认的submit
        event.preventDefault();

        $("#pack_sub").attr('disabled', true);

        //获取数据
        var base_version = $("#base_version").val();
        var model = $("#model").val();
        var pack_uuid_name = $("#pack_uuid").text();
        var md5_uuid_name = $("#md5_uuid").text();
        var pid = $("#pid").val();

        // 校检数据是否为空
        if (!base_version) {
            alert("请输入基础版本号");
            return;
        }
        if (!model) {
            alert("请输入硬件版本号");
            return;
        }

        // 校检数据格式
        var base_version_res = checkBaseVersion(base_version);
        if (!base_version_res) {
            alert("基础版本号应由2位数字以内的数字和小数点组成，且以数字结尾");
            return;
        }

        var model_res = checkModel(model);
        if (!model_res) {
            alert("硬件版本应该由数字、字母、下划线及减号组成");
            return;
        }

        data = {
            "base_version": base_version,
            "model": model,
            "pack_uuid_name": pack_uuid_name,
            "md5_uuid_name": md5_uuid_name,
            "pid": pid
        };

        var con = confirm("确定提交?");
        if (con == true){
            // 使⽤用ajax实现表单的提交行为
            $.ajax({
                url: '/pack/pid_' + pid + '/package',
                type: 'post',
                data: data,
                dataType: 'json',
                headers: { 'X-CSRFToken': csrftoken },
                success: function (response) {
                    if (response.code == '0') {
                        // 添加更新包成功，跳转到当前阅读器所有包展示页面
                        location.href = '/pack/pid_' + pid + '/packages'
                    } else if (response.code == '4102') {
                        alert("登录信息过期");
                        location.href = response.data.to_url
                    } else {
                        alert(response.msg);
                        $("#pack_sub").removeAttr('disabled');
                    }
                }
            });
        }else {
            $("#pack_sub").removeAttr('disabled');
            return
        }

    });
});