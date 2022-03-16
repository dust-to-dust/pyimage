import mysql.connector  # mysql-connector
# 管理工具 HeidiSQL
# 默认用户名是root不是admin


def get_conn():
    try:
        conn = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            passwd='123456',
            database='database',
            auth_plugin='mysql_native_password'
        )
    except mysql.connector.errors.InterfaceError:
        print("Can't connect to MySQL server on '127.0.0.1:3306'")
        exit(1)
        return
    return conn


def select(sql):
    conn = get_conn()
    # print(conn)
    # 表示从数据库中查询时返回的结果是字典的列表
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


# update delete insert
def update(sql, *params):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(sql, params)     # params参数会被execute函数用于补齐sql语句
    cursor.close()
    conn.commit()
    conn.close()
