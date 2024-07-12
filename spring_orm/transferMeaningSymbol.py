# 需要转移的字符
_symbols = {
    "%": "%%"
}


def transfer_meaning(sql):
    """
    特殊字符转义
    """
    sql_tmp = str(sql).lower()
    if "where" in sql_tmp:
        where_idx = sql_tmp.index("where")
        sql_front = sql[:where_idx]

        # where 条件部分转义
        sql_back = sql[where_idx:]
        for k, v in _symbols.items():
            sql_back = sql_back.replace(k, v)
        sql = sql_front + sql_back
    return sql
