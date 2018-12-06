
$(window).load(function () {
    isWork();
});


$(function () {
    // 给所有的查看软件包添加点击事件
    $(".detail").delegate('#package', 'click', function (e) {
        // 获取reversionid
        var rv_id = $(this).parent().prev().val();

        // 获取当前rversionid 下的所有软件包的信息,并填充数据
        $.ajax({
            url: '/pack/packages?rv_id=' + rv_id,
            type: 'get',
            dataType: 'json',
            success: function (response) {
                if (response.code == '0') {
                    // 获取数据成功后替换
                    var packages = response.data;
                    if (1 > packages.length) {
                        $(".pop-shadow").show();
                        $("#pop").show();
                        return;
                    }

                    $('tbody').empty();
                    $.each(packages, function (i, item) {
                        $('tbody').append('<tr>' +
                            '<td>' + item.base_version + '</td>' +
                            '<td>' + item.model + '</td>' +
                            '<td>' + item.pack + '</td>' +
                            '<td>' + item.md5 + '</td>' +
                            '</tr>')
                    });
                    $(".pop-shadow").show();
                    $("#pop").show();
                } else if (response.code == '4102') {
                    alert("登录信息过期");
                    location.href = response.data.to_url
                } else {
                    alert(response.msg);
                }
            }
        });
        e.stopPropagation();
    });
    // 给关闭按钮添加点击事件
    $(".close-ico").click(function (e) {
        $(".pop-shadow").hide();
        $("#pop").hide();
        e.stopPropagation();
    });
    // 实现弹窗拖拽
    $(function () {
        var _move = false;//移动标记
        var _x, _y;//鼠标离控件左上角的相对位置
        $("#pop-title").click(function () {
            //alert("click");//点击（松开后触发）
        }).mousedown(function (e) {
            _move = true;
            _x = e.pageX - parseInt($("#pop").css("left"));
            _y = e.pageY - parseInt($("#pop").css("top"));
            $("#pop").fadeTo(20);//点击后开始拖动并透明显示
            $(this).css('cursor', 'move')
        });
        $(document).mousemove(function (e) {
            if (_move) {
                var x = e.pageX - _x;//移动时根据鼠标位置计算控件左上角的绝对位置
                var y = e.pageY - _y;
                $("#pop").css({ top: y, left: x });//控件新位置
            }
        }).mouseup(function () {
            _move = false;
        });
    });
});