var csrftoken = getCookie('csrftoken');

$(window).load(function () {
    isWork();
});


$(function () {
    $("#faq_del").click(function (e) {
        var url = $(this).prev().attr("href");

        var con = confirm("确定删除吗？"); //在页面上弹出对话框
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

    })
});