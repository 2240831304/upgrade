$(window).load(function () {
    isWork();
});


$(document).ready(function () {
    var csrftoken = getCookie('csrftoken');

    // 获取所有版本号
    function getReaders() {
        $.ajax({
            url: '/pack/readers',
            type: 'get',
            dataType: 'json',
            success: function (response) {
                if (response.code == '0') {
                    // 如果请求成功
                    var oNameSelect = $("#reader_name");
                    var readers = response.data.readers;
                    oNameSelect.empty();
                    oNameSelect.append('<option value="0">--无--</option>');
                    $.each(readers, function (i, item) {
                        oNameSelect.append('<option value="' + item[0] + '">' + item[1] + '</option>')
                    });
                } else if (response.code == '4102') {
                    alert("登录信息过期");
                    location.href = response.data.to_url
                } else {
                    alert(response.msg);
                }
            }
        });
    }

    // 获取对应阅读器的所有已同步版本号
    function getDependVersion(reader_id) {
        $.ajax({
            url: '/pack/rv_' + reader_id + '/rversions/versions',
            type: 'get',
            dataType: 'json',
            success: function (response) {
                if (response.code == '0') {
                    var oVersionSelect = $("#depend_version");
                    var versions = response.data.versions;

                    oVersionSelect.empty();
                    oVersionSelect.append('<option value="0">--无--</option>');
                    $.each(versions, function (i, item) {
                        oVersionSelect.append('<option value="' + item[0] + '">' + item[1] + '</option>')
                    })
                } else if (response.code == '4102') {
                    alert("登录信息过期");
                    location.href = response.data.to_url
                } else {
                    alert(response.msg);
                }
            }
        })
    }


    $(function () {
        // 给添加按钮添加点击事件
        $(".addbtn").click(function (e) {
            var reader_name = $(".reader").val();

            // 校检数据是否存在
            if (!reader_name) {
                alert("请输入阅读器号");
                return;
            }

            // 校检数据格式
            var res = checkReader(reader_name);
            if (!res) {
                alert('阅读器号应由数字、字母、下划线及减号组成');
                return;
            }

            $.ajax({
                url: '/pack/readers',
                type: 'post',
                data: { "reader_name": reader_name },
                dataType: 'json',
                headers: { 'X-CSRFToken': csrftoken },
                success: (function (response) {
                    if (response.code == '0') {
                        alert(response.msg);
                    } else if (response.code == '4102') {
                        alert("登录超时");
                        location.href = response.data.to_url
                    } else {
                        alert(response.msg);
                    }
                })
            });
            e.stopPropagation();
        });

        // 给发布按钮添加点击事件
        $(".pub-reader").click(function (e) {
            $(".pop-shadow").show();
            $("#pop").show();

            // 获取所有的阅读器号
            getReaders();

            //绑定reader_name的change事件
            $("#reader_name").change(function () {
                var reader_id = $(this).val();

                if (reader_id) {
                    // 获取对应
                    getDependVersion(reader_id);
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

        // 给提交按钮添加点击事件
        $("#rversion_sub").click(function (e) {
            var reader_id = $('#reader_name').val();
            var version = $('#version').val();
            var title = $('#v_title').val();
            var depend_version = $('#depend_version').val();
            var description = tinyMCE.getInstanceById('v-description').getBody().innerHTML;


            // 校验参数是否为空
            if (!reader_id) {
                alert("请选择阅读器型号");
                return;
            }
            if (!version) {
                alert("请填写版本号");
                return;
            }
            if (!title) {
                alert("请填写标题");
                return;
            }

            // 校检数据格式
            var res = checkRVersion(version);
            if (!res) {
                alert("阅读器版本只能以三位数以内的数字和小数点组成并且以数字结尾");
                return;
            }

            var data = {
                "reader_id": reader_id,
                "version": version,
                "title": title,
                "depend_version": depend_version,
                "description": description
            };

            $.ajax({
                url: '/pack/rversion',
                type: 'post',
                data: data,
                dataType: 'json',
                headers: { 'X-CSRFToken': csrftoken },
                success: function (response) {
                    if (response.code == '0') {
                        //发布成功后,关闭弹框
                        $(".pop-shadow").hide();
                        $("#pop").hide();
                        location.reload(true);
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

        // 给同步更新 编辑 查看 删除添加点击事件,使用事件委托
        $('table').delegate('#is_update', 'click', function (e) {
            var rv_id = $(this).parent().parent().find("#rv_id").val();

            var con = confirm("确定同步更新吗？"); //在页面上弹出对话框
            if (con == true) {
                $.ajax({
                    url: '/pack/rversion/state',
                    type: 'put',
                    data: { "rv_id": rv_id },
                    dataType: 'json',
                    headers: { 'X-CSRFToken': csrftoken },
                    success: function (response) {
                        if (response.code == '0') {
                            //更新成功后，按钮不能点击，编辑按钮变成点击按钮
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


            e.stopPropagation();
        }).delegate('#edit', 'click', function (e) {
            var rv_id = $(this).parent().parent().find("#rv_id").val();
            location.href = '/pack/rversion/rv_'+rv_id
        }).delegate('#history', 'click', function (e) {
            var reader_id = $(this).parent().parent().find("#reader_id").val();
            location.href = '/pack/rv_' + reader_id + '/rversions'
        });

        // 目前不需要，可以以后会需要
        // $('table').delegate('#del', 'click', function (e) {
        //     var rv_id = $(this).parent().parent().find("#rv_id").val();
        //     $.ajax({
        //         url: '/pack/reader',
        //         type: 'delete',
        //         data: { "rv_id": rv_id },
        //         dataType: 'json',
        //         headers: { 'X-CSRFToken': csrftoken },
        //         success: function (response) {
        //             if (response.code == '0') {
        //                 //删除成功后，刷新页面
        //                 location.reload(true)
        //             } else {
        //                 alert(response.msg)
        //             }
        //         }
        //     });
        // })
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


