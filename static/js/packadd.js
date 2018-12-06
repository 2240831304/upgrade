var csrftoken = getCookie('csrftoken');

$(window).load(function () {
    isWork();
});


$(function () {
    $('#pack_info').submit(function (event) {
        // 阻⽌止表单默认的submit
        event.preventDefault();

        //获取数据
        var base_version = $("#base_version").val();
        var model = $("#model").val();
        var pack_con = $("#pack_con").val();
        var md5_con = $("#md5_con").val();
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
        if (!pack_con) {
            alert("请选择更新包");
            return;
        }
        if (!md5_con) {
            alert("请选择md5文件");
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

        // 使⽤用ajax实现表单的提交行为
        $(this).ajaxSubmit({
            url: '/pack/pid_' + pid + '/package',
            type: 'post',
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
                }
            }
        });
    });
});