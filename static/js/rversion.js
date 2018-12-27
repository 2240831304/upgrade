var csrftoken = getCookie('csrftoken');

$(window).load(function () {
    var content = $('#textarea_tmp').val();
    tinyMCE.getInstanceById('description').getBody().innerHTML = content;

    isWork();
});

$(function () {
    $("#rversion_sub").click(function (e) {
        var rv_id = $("#rv_id").val();
        var reader_id = $('#reader_name').prev().val();
        var version = $('#version').val();
        var title = $('#v-title').val();
        var description = tinyMCE.getInstanceById('description').getBody().innerHTML;
        var depend_version = $('#depend_version').val();

        // 校检是否有值
        if (!reader_id) {
            alert('请输入阅读器号');
            return;
        }
        if (!version) {
            alert('请输入版本号');
            return;
        }

        if (!title) {
            alert('请输入标题');
            return;
        }

        // 校检数据格式
        var res = checkRVersion(version);
        if (!res){
            alert("阅读器版本只能以三位数以内的数字和小数点组成并且以数字结尾,同时组数不超过三组");
            return;
        }

        //组织参数
        data = {
            "reader_id": reader_id,
            "version": version,
            "title": title,
            "description": description,
            "depend_version": depend_version
        };
        // 发送请求
        $.ajax({
            url: '/pack/rversion/rv_'+rv_id,
            type: 'put',
            data: data,
            dataType: 'json',
            headers: { 'X-CSRFToken': csrftoken },
            success: function (response) {
                if (response.code == '0') {
                    //编辑成功
                    location.href = response.data.to_url
                } else if (response.code == '4102') {
                    alert("登录信息过期");
                    location.href = response.data.to_url
                } else {
                    alert(response.msg);
                }
            }
        })
    })
});