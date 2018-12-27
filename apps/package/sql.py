# 查询test数据库中已同步更新的对应reader_id版本的所有rversion对象,并按照版本号升序
test_order_update_rv = "SELECT * FROM test_fill_rversion WHERE reader_id = %s AND state = %s ORDER BY vcode"

# 获取所有未删除的阅读器号的最新版本对象
test_each_newest_rvs = "SELECT * FROM test_fill_rversion " \
                 "INNER JOIN " \
                 "(SELECT reader_id, MAX(vcode) AS max_vcode FROM test_fill_rversion GROUP BY reader_id) as max_rversion " \
                 "ON test_fill_rversion.reader_id=max_rversion.reader_id AND test_fill_rversion.vcode=max_rversion.max_vcode " \
                 "ORDER BY update_time DESC "

# 查询test数据库中对应reader_id的最新的rversion对象
test_newest_rv = "select * from test_fill_rversion WHERE reader_id=%s ORDER BY vcode DESC LIMIT 1"

# 获取对应pid比依赖版本高的基础版本号 包对象
test_get_rv_gte_depend_package = "select * from test_fill_package where pid=%s AND p_vcode >= %s"

# 获取对应阅读器版本的所有未删除的升级包信息，并按基础版本号和model排序
test_get_rv_packages_not_delete = "select * from test_fill_package WHERE pid=%s AND test_fill_package.state!=%s ORDER BY p_vcode, model"