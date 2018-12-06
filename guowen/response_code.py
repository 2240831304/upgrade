class HTTPCODE(object):
    OK                     = 200
    CREATED                = 201
    ACCEPTED               = 202
    NOCONTENT              = 204
    RESETCONTENT           = 205

    MOVEDPERMANENTLY       = 301
    SEEOTHER               = 303
    NOTMODIFIED            = 304

    BADREQUEST             = 400
    UNAUTHORIZED           = 401
    FORBIDDEN              = 403
    NOTFOUND               = 404
    METHODNOTALLOWED       = 405
    NOTACCEPTABLE          = 406
    REQUESTTIMEOUT         = 408
    CONFLICT               = 409
    GONE                   = 410
    LENGTHREQUIRED         = 411

    INTERNALSERVERERROR    = 500
    SERVICEUNAVAILABLE     = 503


class CODE(object):
    OK                     = 0
    DBERR                  = 4001
    NODATA                 = 4002
    DATAEXIST              = 4003
    DATAERR                = 4004
    SESSIONERR             = 4101
    LOGINERR               = 4102
    PARAMERR               = 4103
    USERERR                = 4104
    ROLEERR                = 4105
    VERIFICATIONERR        = 4106
    EMAILERR               = 4107
    REQERR                 = 4201
    IPERR                  = 4202
    THIRDERR               = 4301
    IOERR                  = 4302
    SERVERERR              = 4500
    UNKOWNERR              = 4501

class RET(object):
    OK                     = 0
    MODELERR               = 1
    DEVICEERR              = 1001
    VERSIONERR             = 1004
    ACTIONERR              = 1007
    ENCODINGERR            = 3100




error_map = {
    HTTPCODE.OK                     : "请求成功",
    HTTPCODE.CREATED                : "创建成功",
    HTTPCODE.ACCEPTED               : "更新成功",
    HTTPCODE.NOCONTENT              : "无内容，在没有新文档的情况下，确保浏览器继续显示先前的文档",
    HTTPCODE.RESETCONTENT           : "重置内容,强迫浏览器清除表单域",

    HTTPCODE.MOVEDPERMANENTLY       : "资源的URI已被更新，新URL在响应头信息中",
    HTTPCODE.SEEOTHER               : "其他（如，负载均衡)",
    HTTPCODE.NOTMODIFIED            : "缓冲的版本已经被更新，客户端应刷新文档",

    HTTPCODE.BADREQUEST             : "错误请求（如，参数错误）",
    HTTPCODE.UNAUTHORIZED           : "未授权，表示客户端在授权头信息中没有有效的身份信息时访问受到密码保护的页面",
    HTTPCODE.FORBIDDEN              : "被禁止访问",
    HTTPCODE.NOTFOUND               : "请求的资源不存在",
    HTTPCODE.METHODNOTALLOWED       : "请求方法对指定的资源不适用",
    HTTPCODE.NOTACCEPTABLE          : "请求格式错误",
    HTTPCODE.REQUESTTIMEOUT         : "请求超时",
    HTTPCODE.CONFLICT               : "通用冲突, 试图上传版本不正确的文件",
    HTTPCODE.GONE                   : "已经不存在，文档被移走的情况下使用",
    HTTPCODE.LENGTHREQUIRED         : "需要数据长度",

    HTTPCODE.INTERNALSERVERERROR    : "内部错误",
    HTTPCODE.SERVICEUNAVAILABLE     : "服务当前无法处理请求",

    CODE.OK                    : "响应正常",
    CODE.DBERR                 : "数据库查询错误",
    CODE.NODATA                : "无数据",
    CODE.DATAEXIST             : "数据已存在",
    CODE.DATAERR               : "数据错误",
    CODE.SESSIONERR            : "用户未登录",
    CODE.LOGINERR              : "用户登录失败",
    CODE.PARAMERR              : "参数错误",
    CODE.USERERR               : "用户不存在，未激活",
    CODE.ROLEERR               : "用户身份错误",
    CODE.VERIFICATIONERR       : "验证错误",
    CODE.REQERR                : "非法请求或请求次数受限",
    CODE.IPERR                 : "IP受限",
    CODE.THIRDERR              : "第三方系统错误",
    CODE.IOERR                 : "文件读写错误",
    CODE.SERVERERR             : "内部错误",
    CODE.UNKOWNERR             : "未知错误",
    
    RET.OK                     : "响应正常",
    RET.MODELERR               : "硬件版本信息错误",
    RET.DEVICEERR              : "序列号错误",
    RET.VERSIONERR             : "版本号错误",
    RET.ACTIONERR              : "请求接口错误",
    RET.ENCODINGERR            : "编码格式错误",
}
