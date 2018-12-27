# 查询用户数据库中已同步更新的对应reader_id版本的最新的
newest_rv = "SELECT * FROM fill_rversion WHERE reader_id = %s AND state =2 ORDER BY vcode LIMIT 1"
