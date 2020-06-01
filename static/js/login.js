$(document).ready(function(){
    $('.form-login').submit(function (event) {
        // 阻止form表单自己的提交事件
        event.preventDefault();
        var username = $('#username').val();
        var passwd = $('#passwd').val();
        passwd = sha1(passwd);
        // 校验是否有值
        if (!username) {
            $("#error-msg p").html("******用户名不能为空******");
            $("#error-msg p").show();
            return;
        }
        if (!passwd) {
            $('#error-msg p').html('******密码不能为空******');
            $('#error-msg p').show();
            return;
        }
        var csrftoken = getCookie('csrftoken');

        var data = {
            'username': username,
            'passwd': passwd
        };

        // 发送登录请求给服务器
        $.ajax({
            url: '/user/login',
            type: 'post',
            data: data,
            dataType: 'json',
            headers: {'X-CSRFToken': csrftoken},
            success: function (response) {
                if (response.code == '0') {
                    // 如果登录成功，进入到主页
                    location.href = response.data.to_url
                } else {
                    $('#error-msg p').html('用户名或密码错误');
                    $('#error-msg p').show();
                }
            }
        });
    });
});

