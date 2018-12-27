// 获取cookie
function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

// 校验阅读器型号
function checkReader(reader_name) {
    // 数字，字母，下划线，中划线
    var reg = new RegExp("^[a-zA-Z0-9_-]+$");
    res = reg.test(reader_name);
    return res
}

// 校验阅读器版本号
function checkRVersion(rversion) {
    var reg = new RegExp("^((?!0)(?:[0-9]{1,3})\\.)(((?!0)(?:[0-9]{1,3})|0)\\.)?((?!0)(?:[0-9]{1,3})|0)$");
    res = reg.test(rversion);
    return res
}

// 校验基础版本号
function checkBaseVersion(base_version) {
    var reg = new RegExp("^(?!0)(?:[0-9]{1,2})\\.0$");
    res = reg.test(base_version);
    return res
}


// 校验硬件型号
function checkModel(model) {
    var reg = new RegExp("^[a-zA-Z0-9_-]+$");
    res = reg.test(model);
    return res
}

// 校验用户是否在操作
function isWork() {
    var int;
    var flag = false;

    function setflag() {
        flag = !flag;
        isinte();
    }

    function isinte() {
        if (flag) {
            setinte();
        } else {
            stopinte();
            setflag();
        }
    }

    function setinte() {
        //setInternal:第一次执行时，会先等待指定的时间，然后才执行相应的函数
        int = setInterval(settime, 10*60*1000);
    }
    function stopinte() {
        clearInterval(int);
    }
    function settime() {
        stopinte();
        location.href = "/user/logout";
    }
    //获取鼠标点击事件
    $(document).click(function () {
        setflag();
    });

    //获取鼠标移动事件
    $(document).mousemove(function (event) {
        setflag();
    });

    //获取键盘事件
    $(document).keydown(function () {
        setflag();
    });
    $(function () {
        setflag();
    })
}