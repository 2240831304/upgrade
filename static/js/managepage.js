

function selectrequest() {
    var csrftoken = getCookie('csrftoken');

    var devicetype = $('#devicetype').val();
    if (!devicetype) {
        alert("请输入设备的类型");
        return;
    }

    var type = null;
    var item = null;
    var obj = document.getElementsByName("versionradio");
    for (var i = 0; i < obj.length; i++) { //遍历Radio
      if (obj[i].checked) {
           item = obj[i].value;
      }
    }
    if (item == "testradio"){
        type = "test";
    } else if (item == "officialradio"){
        type = "official";
    } else {
        alert("请选择查询测试版本,或正式版本");
        return;
    }

    var data = {
        "type":type,
        "device":devicetype
    };
    //console.debug(data);

    $.ajax({
        url: '/android/versionmanagesys',
        type: 'get',
        data: data,
        dataType: 'json',
        //headers: {'action': 'softwareupgrade'},
        headers: {'X-CSRFToken': csrftoken},
        success: function (response) {
            if (response.code == '0') {
                //location.href = response.data.to_url
                var data = response.data;
                console.debug(data);
                if (!data){
                    alert("当前设备类型暂时没有发布版本");
                }
            } else {
                window.alert(response.msg);
            }
        }
    });

}