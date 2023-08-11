from flask import Flask,request
import requests
from flask_cors import *
import time
from lxml import etree
import sqlConn
from crawler import Resourcefrom
from bs4 import BeautifulSoup
import re
import json



app = Flask(__name__)
CORS(app, supports_credentials=True)#解决flask中的跨域问题

@app.route('/zhihu_app', methods=['POST'])
def zhihu_app(url_list):
    data = request.get_data()
    task_id =  data.decode('utf-8')
    sorce='zhihu'
    # 连接数据库、创建表、返回sql插入语句
    conn, cursor, sql= sqlConn.connect_mysql()
    # 爬取知乎api中的问答链接
    headers = {
        'x-api-version': '3.0.89',
        'x-app-version': '5.26.2',
        'x-app-za': 'OS=Android&Release=8.0.0&Model=SM-G9500&VersionName=5.26.2&VersionCode=913&Product=com.zhihu.android&Width=1080&Height=2076&Installer=%E5%BA%94%E7%94%A8%E5%AE%9D&DeviceType=AndroidPhone&Brand=samsung',
        'x-app-flavor': 'myapp',
        'x-app-build': 'release',
        'x-network-type': 'WiFi',
        'Host': 'api.zhihu.com',
        'User-Agent': 'com.zhihu.android/Futureve/5.26.2 Mozilla/5.0 (Linux; Android 8.0.0; SM-G9500 Build/R16NW; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/67.0.3396.87 Mobile Safari/537.36',
        'Connection': 'keep-alive'
    }
    if len(url_list)== 1:
        r = requests.get(url_list[0], headers=headers).json()['data']
    else:
        r = url_list


    for each in r:
        title = each['target']['title_area']['text']
        card_id = list(str(each['target']['link']['url']).split('/'))[-1]
        q_url = 'https://api.zhihu.com/v4/questions/' + card_id + '/answers?order_by=&show_detail=1'
        question_url='https://www.zhihu.com/question/'+card_id

        try:

            for i in range(0, 20, 5):
                params = {'offset': i}
                res = requests.get(q_url, headers=headers, params=params).json()['data']
                for item in res:
                    crawlertime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    timestamp = item['created_time']
                    createtime = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp)))
                    author = item['author']['name']
                    content = item['excerpt']
                    cursor.execute(sql, (crawlertime,title,createtime,author,content,sorce,question_url,task_id))
                conn.commit()
        except Exception as e:
            print(f"{q_url}:{e}")

    conn.close()
    cursor.close
    return 'ok'


@app.route('/CSDN', methods=['POST'])
def CSDN(url_list):
    conn, cursor, sql= sqlConn.connect_mysql()
    sorce= 'CSDN'
    data = request.get_data()
    task_id =  data.decode('utf-8')
    xpath_str = '//div[@class="content"]/a/@href'
    if len(url_list)== 1:
        r = Resourcefrom.reuturn_urlpoolist(url_list[0], xpath_str)
    else:
        r = url_list
    title_xpath = '//h1[@class="title-article" and @id="articleContentId"]/text()'
    content_xpath = '//div[@id="content_views"]//h1 | //div[@id="content_views"]//h2 | //div[@id="content_views"]//h3 | //div[@id="content_views"]//h4 | //div[@id="content_views"]//h5 | //div[@id="content_views"]//h6 | //div[@id="content_views"]//p'
    author_xpath = '//*[@id="mainBox"]/main/div[1]/div[1]/div/div[2]/div[1]/div/a[1]/text()'
    createtime_xpath = '//span[@class="time"]/text()'

    for i in range(1, len(r)):
        url_blog = r[i]
        try:
            title = Resourcefrom.reuturn_urlpoolist(url_blog, title_xpath)
            content_elements = Resourcefrom.reuturn_urlpoolist(url_blog, content_xpath)
            content = "\n".join([element.text.strip() for element in content_elements if element.text])
            author = Resourcefrom.reuturn_urlpoolist(url_blog,author_xpath)
            createtime_text = Resourcefrom.reuturn_urlpoolist(url_blog, createtime_xpath)[0]
            createtime = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', createtime_text).group()
            crawlertime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            cursor.execute(sql, (
                crawlertime,
                title,
                createtime,
                author,
                content,
                url_blog,
            ))
            conn.commit()
        except Exception as e:
            print(f"{url_blog}:{e}")
            continue
    conn.close()
    return 'ok'

@app.route('/url_pool', methods=['POST'])
def url_zhihu():
    sorce= 'zhihu'
    data = request.get_data()
    task_id =data.decode('utf-8')
    conn, cursor, sql= sqlConn.connect_mysql()
    e_sql="select pramater from crawler_task where id="+task_id
    cursor.execute(e_sql)
    url_list=cursor.fetchall()
    url_list=url_list[0][0].split('\r\n')

    xpath_str = '//div[@class="RichText ztext Post-RichText css-1g0fqss"]//p[@data-pid]/a/@href'
    if len(url_list)== 1:
        r = Resourcefrom.reuturn_urlpoolist(url_list[0], xpath_str)
    else:
        r = url_list
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
    }
    print(type(r))
    p=0
    length = len(r)
    for q_url in r:
        p += 1
        opercentage = float((p / length) * 100)
        percentage=round(opercentage,2)

        print(p,length,percentage)
        # time.sleep(1)
        update="update crawler_task set progress=+" + str(percentage) +" where id=" +task_id
        cursor.execute(update)
        conn.commit()
        question_id = q_url.split('/')[-1]

        url = 'https://api.zhihu.com/v4/questions/' + question_id + '/answers?order_by=&show_detail=1'

        # 请求头
        api_headers = {
            'x-api-version': '3.0.89',
            'x-app-version': '5.26.2',
            'x-app-za': 'OS=Android&Release=8.0.0&Model=SM-G9500&VersionName=5.26.2&VersionCode=913&Product=com.zhihu.android&Width=1080&Height=2076&Installer=%E5%BA%94%E7%94%A8%E5%AE%9D&DeviceType=AndroidPhone&Brand=samsung',
            'x-app-flavor': 'myapp',
            'x-app-build': 'release',
            'x-network-type': 'WiFi',
            'Host': 'api.zhihu.com',
            'User-Agent': 'com.zhihu.android/Futureve/5.26.2 Mozilla/5.0 (Linux; Android 8.0.0; SM-G9500 Build/R16NW; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/67.0.3396.87 Mobile Safari/537.36',
            'x-udid': 'AIDAlfY0qguPTkq2Y0YbY0qgqg2Y0qg2Y0g2Y0g',
        }
        try:
            crawlertime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            for i in range(0, 20, 5):
                params = {'offset': i}
                r = requests.get(url, headers=api_headers, params=params).json()
                # res = json.loads(r.text)
                for item in r['data']:
                    title = item['question']['title']
                    author = item['author']['name']
                    content = item['excerpt']
                    createtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['created_time']))
                    cursor.execute(sql, (crawlertime, title, createtime, author, content, sorce, q_url, task_id))
                    conn.commit()
        except Exception as e:
            print(f"{q_url}:{e}")
        continue
    conn.close()
    return 'ok'





if __name__ == '__main__':
    app.run()
    app.run(debug=True)
    #外部可访问的服务器
    # app.run(host='0.0.0.0')
