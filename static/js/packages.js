var csrftoken = getCookie('csrftoken');

$(window).load(function () {
    isWork();
});

$(function () {
    $('table').delegate("#pack_edit", 'click', function (e) {
        var pid = $(this).attr('pid');
        var pack_id = $(this).attr('pack_id');
        location.href = '/pack/pid_' + pid + "/package/pack_" + pack_id
    }).delegate('#pack_del', 'click', function (e) {
        var pid = $(this).prev().attr('pid');
        var pack_id = $(this).prev().attr('pack_id');
        url = '/pack/pid_' + pid + "/package/pack_" + pack_id;
        var con = confirm("确定删除吗？");
        if (con == true) {
            $.ajax({
                url: url,
                type: 'delete',
                dataType: 'json',
                headers: { 'X-CSRFToken': csrftoken },
                success: function (response) {
                    if (response.code == '0') {
                        //删除成功后，刷新页面
                        location.reload(true)
                    } else if (response.code == '4102') {
                        alert("登录信息过期");
                        location.href = response.data.to_url
                    } else {
                        alert(response.msg);
                    }
                }
            });
        } else {
            return;
        }

    });
});

