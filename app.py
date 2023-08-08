from flask import Flask,request
import requests
from flask_cors import *
import time
from crawler import Best100


app = Flask(__name__)
CORS(app, supports_credentials=True)#解决flask中的跨域问题

@app.route('/best100', methods=['POST'])
def best100():
    # 创建zhihu_question数据表
    create_table_sql = '''
    CREATE TABLE IF NOT EXISTS zhihu_question (
        id INT AUTO_INCREMENT PRIMARY KEY,
        url VARCHAR(255),
        title VARCHAR(255),
        answer_count INT,
        author VARCHAR(100),
        voteup_count INT,
        comment_count INT,
        update_time DATETIME
    )
    '''
    update_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['updated_time']))
    conn,cusor = sqlConn.connect_mysql(create_table_sql)
    url = 'https://zhuanlan.zhihu.com/p/20751140'
    xpath_str = '//div[@class="RichText ztext Post-RichText css-1g0fqss"]//p[@data-pid]/a/@href'
    data = Resourcefrom.reuturn_urlpoolist(url, xpath_str)
    return data






if __name__ == '__main__':
    # app.run()
    app.run(debug=True)
    #外部可访问的服务器
    # app.run(host='0.0.0.0')
