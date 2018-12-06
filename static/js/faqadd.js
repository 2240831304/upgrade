var csrftoken = getCookie('csrftoken');

$(window).load(function () {
    isWork();
});


$(function () {
    $('#faq_sub').click(function (event) {

        //获取数据
        var question = $("#question").val();
        var answer = tinyMCE.getInstanceById('answer').getBody().innerHTML;


        // 校检数据是否为空
        if (!question) {
            alert("请输入问题");
            return;
        }
        if (!answer) {
            alert("请输入解答");
            return;
        }

        data = {
            "question": question,
            "answer": answer
        };

        // 使⽤用ajax实现表单的提交行为
        $.ajax({
            url: '/faq/faq',
            type: 'post',
            data: data,
            dataType: 'json',
            headers: { 'X-CSRFToken': csrftoken },
            success: function (response) {
                if (response.code == '0') {
                    // 添加新成功，跳转到faq展示页面
                    location.href = '/faq/faqs'
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