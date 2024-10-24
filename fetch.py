from flask import Flask, request, render_template
import requests
from datetime import datetime  # 导入 datetime 模块
import mysql.connector

app = Flask(__name__)

# 设置数据库连接
db_config = {
    'user': 'cy_1',
    'password': 'Chen050506',
    'host': 'localhost',
    'database': 'ip'
}

# 使用 mysql.connector 连接数据库
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()


# 定义获取地理位置信息的函数
def get_geo_info(ip):
    try:
        response = requests.get(f'http://ip-api.com/json/{ip}?lang=zh-CN')
        return response.json()
    except Exception as e:
        return None


@app.route('/cy', methods=['GET'])
def count_visitors():
    # 获取访问者的 IP 地址
    def get_client_ip(request):
        if 'X-Forwarded-For' in request.headers:
            # 如果有 X-Forwarded-For 头，取第一个 IP
            return request.headers['X-Forwarded-For'].split(',')[0]
        else:
            # 否则，直接使用 remote_addr
            return request.remote_addr

    visitor_ip = get_client_ip(request)
    geo_info = get_geo_info(visitor_ip)

    # 获取当前时间
    visit_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if geo_info and geo_info.get('status') == 'success':
        query = """
        INSERT INTO ip_info (ip_address, city, region_name, latitude, longitude, visit_time)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        data = (
            visitor_ip,
            geo_info.get('city', '未知'),
            geo_info.get('regionName', '未知'),
            geo_info.get('country', '未知'),
            geo_info.get('lat', '未知'),
            geo_info.get('lon', '未知'),
            visit_time
        )
    else:
        query = """
        INSERT INTO ip_info (ip_address, city, region_name, latitude, longitude, visit_time)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        data = (
            visitor_ip,
            '未知',
            '未知',
            '未知',
            '未知',
            '未知',
            visit_time
        )

    cursor.execute(query, data)
    conn.commit()  # 提交到数据库

    cursor.close()
    conn.close()  # 关闭数据库连接

    return render_template('hello.html')


@app.route('/sfh', methods=['GET'])
def show_ips():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)  # 使用字典游标

    cursor.execute("SELECT * FROM ip ORDER BY visit_time DESC")  # 查询访客信息
    infos = cursor.fetchall()  # 获取所有结果

    cursor.close()
    conn.close()

    return render_template('visitor_ips.html', infos=infos)  # 将结果传递给模板


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1215)
