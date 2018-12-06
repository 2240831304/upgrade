var csrftoken = getCookie('csrftoken');

$(window).load(function () {
    var content = $('#answer_tmp').val();
    tinyMCE.getInstanceById('answer').getBody().innerHTML = content;
    isWork();
});


$(function () {
    $('#faq_sub').click(function (event) {

        //获取数据
        var question = $("#question").val();
        var answer = tinyMCE.getInstanceById('answer').getBody().innerHTML;
        var faq_id = $("#faq_id").val();


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
            "answer": answer,
            "faq_id": faq_id
        };

        // 使⽤用ajax实现表单的提交行为
        $.ajax({
            url: '/faq/faq/' + faq_id,
            type: 'put',
            data: data,
            dataType: 'json',
            headers: { 'X-CSRFToken': csrftoken },
            success: function (response) {
                if (response.code == '0') {
                    // 修改成功，跳转到faq展示页面
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