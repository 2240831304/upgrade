

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
                //console.debug(data);
                if (!data){
                    alert("当前设备类型暂时没有发布版本");
                    cleartableitem();
                    $("#tipmessage p").hide();
                }else {
                    addversionitem(data);
                }

            } else {
                window.alert(response.msg);
                $("#tipmessage p").hide();
                cleartableitem();
            }
        }
    });

}

function cleartableitem() {
    var tb = document.getElementById('versiontable');
    var rowNum = tb.rows.length;
    for (var i=1;i<rowNum;i++)
    {
        tb.deleteRow(i);
        rowNum = rowNum-1;
        i = i-1;
    }
}


function addversionitem(versionlist) {
    //console.debug(versionlist);

    cleartableitem();

    var limitShowRow = 0;
    if (versionlist.length >= 12){
        limitShowRow = 12;
    } else {
        limitShowRow = versionlist.length;
    }

    for (var i = 0;i < limitShowRow ;i++){
        var item = versionlist[i];
        var str = "<tr>\n" +
        "<td id='devicetypetd'>%1</td>\n" +
        "<td id='versiontd'>%2</td>\n" +
        "<td>%3</td>\n" +
        "<td><button id='deleterowbut' name='button' value=%4 onclick='deleteversion(this)'>删除</button></td>\n" +
        "</tr>";

        str = str.replace("%1",item["device"]);
        str = str.replace("%2",item["version"]);
        str = str.replace("%3",item["publishtime"]);
        str = str.replace("%4",item["version"]);
        $('#versiontable').append($(str));
    }

    $("#tipmessage p").html("***只显示最近12次的升级版本***");
    $("#tipmessage p").show();
}


function deleteversion(data) {

    //console.debug(data);
    //console.debug(data.name,data.value);
    var tb = document.getElementById('versiontable');
    var rowNum = tb.rows.length;
    var rows = tb.rows;

    var devicever = "";
    var rowindex = 0;
    for (var i = 1;i<rowNum;i++)
    {
        //console.debug(rows[i].cells[1].innerHTML)
        var versioncmp = rows[i].cells[1].innerHTML;
        if(versioncmp == data.value){
            devicever = versioncmp;
            rowindex = i;
            //tb.deleteRow(i);
            break;
        }
    }

    var devicetype = $('#devicetype').val();
    if (!devicetype) {
        alert("未获取到要删除版本的设备类型");
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
        alert("未获取到要删除测试版本,or正式版本");
        return;
    }

    var deletemesage = "确定要删除设备:" + devicetype + " 版本号：" + devicever;
    deletemesage += "服务器上的版本吗？";

    if(window.confirm(deletemesage)){
        executedeleterequest(type,devicetype,devicever,rowindex);
    } else {
        return;
    }

}


function executedeleterequest(type,devicetype,versionnum,rowindex) {
    var csrftoken = getCookie('csrftoken');

    var data = {
        "type":type,
        "device":devicetype,
        "version":versionnum
    };

    $.ajax({
        url: '/android/versionmanagesys',
        type: 'post',
        data: data,
        dataType: 'json',
        headers: {'X-CSRFToken': csrftoken},
        success: function (response) {
            if (response.code == '0') {
                window.alert("服务器删除版本成功");
                var tb = document.getElementById('versiontable');
                tb.deleteRow(rowindex);
            } else {
                window.alert("服务器删除版本失败，请重新删除");
            }
        }
    });

}