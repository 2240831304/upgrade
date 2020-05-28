

function handle() {
    //window.alert("111");
    //console.debug("123")
    var csrftoken = getCookie('csrftoken');

    $.ajax({
        url: '/android/pushlishtest',
        type: 'post',
        //data: data,
        //dataType: 'json',
        //headers: {'action': 'softwareupgrade'},
        headers: {'X-CSRFToken': csrftoken},
        success: function (response) {
            if (response.code == '0') {
                // swsw
                location.href = response.data.to_url
            } else {
                window.alert("111");
            }
        }
    });


}