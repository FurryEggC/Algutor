import pymysql

"""
CREATE DATABASE knowledge_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'knowledge_user'@'localhost' IDENTIFIED BY 'strong_password_123';
GRANT ALL PRIVILEGES ON knowledge_db.* TO 'knowledge_user'@'localhost';
FLUSH PRIVILEGES;
"""


try:
    connection = pymysql.connect(
        host='localhost',
        user='knowledge_user',
        password='strong_password_123',
        database='knowledge_db',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    print("连接成功!")
    connection.close()
except Exception as e:
    print(f"连接失败: {e}")
