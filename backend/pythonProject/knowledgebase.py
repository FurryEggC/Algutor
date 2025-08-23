from flask import Flask

app = Flask(__name__)

@app.route("/data")
def getFromDatabase() :
    import pymysql

    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root123', charset='utf8', db='knowledge')
    cursor = conn.cursor()



