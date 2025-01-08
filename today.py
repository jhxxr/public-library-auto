import json
import pymysql
from datetime import datetime, timedelta, date
import time
import requests
import concurrent.futures
import returnkey
#import ssl
import random


# 数据库管理类
class DatabaseManager:
    def __init__(self):


        # 在初始化时连接数据库
        self.conn = pymysql.connect(
            host='',
            port=4000,
            user='',
            password='',
            db='yuyue',
        )

        # 创建游标
        self.cursor = self.conn.cursor()

    # 获取所有用户数据
    def fetch_all_users(self):
        self.cursor.execute("SELECT * FROM users")
        return self.cursor.fetchall()
    def update_user(self, user):
        # 构建 SQL 语句的部分
        sql_update_parts = ["{} = %s".format(key) for key in user.keys()]
        sql_update = "UPDATE users SET " + ", ".join(sql_update_parts) + " WHERE name = %s"

        # 构建参数列表
        update_values = list(user.values())
        update_values.append(user['name'])
        print(sql_update)
        print(update_values)
        # 执行 SQL 语句
        self.cursor.execute(sql_update, update_values)
        self.conn.commit()

    # 关闭数据库连接
    def close(self):
        self.cursor.close()
        self.conn.close()

# 座位预约类
class SeatReservation:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.today = date.today()
        self.tomorrow = self.today + timedelta(days=1)

    def generate_timestamp(self):
        # 获取当前时间的秒数
        current_time_seconds = time.time()

        # 将秒数转换为毫秒，并转换为整数
        timestamp_milliseconds = int(current_time_seconds * 1000)

        return timestamp_milliseconds

    def login(self,username, password):
        logi = f'https://leosys.cn/cczukaoyan/rest/auth?username={username}&password={password}'
        key = returnkey.xcode("GET")
        random_delay = random.uniform(0.2, 1)
        time.sleep(random_delay)#随机延时
        X_request_id = key[0]
        X_request_date = key[1]
        X_hmac_request_key = key[2]
        headers = {
            'Host': 'leosys.cn',
            'X-request-date': X_request_date,
            'loginType': 'APPLET',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090819) XWEB/8531',
            'actCode': 'true',
            'Content-Type': 'application/json',
            'xweb_xhr': '1',
            'X-hmac-request-key': X_hmac_request_key,
            'user_ip': '1.1.1.1',
            'token': "",
            'X-request-id': X_request_id,
            'Accept': '*/*',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://servicewechat.com/wx8adafd853fc21fd6/82/page-frame.html',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }

        try:
            response = requests.get(logi, headers=headers)
            print(response.text)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"请求错误: {e}")
            return {"error": "登录失败或响应中缺少所需数据"}

        try:
            raw_json = response.json()
        except ValueError:
            print("解析JSON失败")
            return {"error": "登录失败或响应中缺少所需数据"}

        # 检查是否存在必要的数据
        if raw_json is not None and 'data' in raw_json and raw_json['data'] is not None and 'token' in raw_json['data']:
            return raw_json['data']['token']
        else:
            print("响应中缺少所需数据")
            return {"error": "登录失败或响应中缺少所需数据"}



    def get_first_ID(self, user_token,user_name):
        url = 'https://leosys.cn/cczukaoyan/rest/v2/history/1/50?page=1'
        key = returnkey.xcode("GET")
        X_request_id = key[0]
        X_request_date = key[1]
        X_hmac_request_key = key[2]
        #获取现在时间戳
        #timestamp = self.generate_timestamp()
        headers = {
            'Host': 'leosys.cn',
            'Connection': 'keep-alive',
            'X-request-date': X_request_date,
            'loginType': 'APPLET',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x6309092b) XWEB/9053',
            'Content-Type': 'application/json',
            'xweb_xhr': '1',
            'X-hmac-request-key': X_hmac_request_key,
            'user_ip': '1.1.1.1',
            'token': user_token,
            'X-request-id': X_request_id,
            'Accept': '*/*',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://servicewechat.com/wx8adafd853fc21fd6/82/page-frame.html',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json().get('data', {})
            print(data)
            reserved_id = 0
            today_start_time = "0:00"
            today_end_time = "0:00"
            loc = 0
            for reservation in data['reservations']:
                if reservation['stat'] == "RESERVE" :
                        print(reservation)

                        reserved_id = reservation['id']
                        today_start_time = reservation['begin']
                        today_end_time = reservation['end']
                        loc = reservation['loc']
                        break
                elif reservation['stat'] == "CHECK_IN":
                    reserved_id = -1
                    today_start_time = reservation['begin']
                    today_end_time = reservation['end']
                    loc = reservation['loc']
                    break
  

            
            return {
                "name": user_name,
                "bookid": reserved_id,
                "startTime": today_start_time.split(":")[0],
                "endTime": today_end_time.split(":")[0],
                "loc": loc,
                "status": "未预约" if reserved_id == 0 else "未签到" if reserved_id > 0 else "已签到"
            }





    def if_book(self, user):
            results = []
            # Extract user details
            username = user["account"]
            password = user["password"]
            # X_request_date = user["X_request_date"]
            # X_hmac_request_key = user["X_hmac_request_key"]
            # login_token = user["login_token"]
            # X_request_id = user["X_request_id"]

            # Log in and get token
            user_token_result = self.login(username, password)
            if "error" in user_token_result:
                # 重复登录
                user_token_result = self.login(username, password)
                if "error" in user_token_result:
                    return None
                

            # 继续执行预约操作
            #booking_result = self.checkin(user_token_result)
            booking_result = self.get_first_ID(user_token_result,user["name"])
        
            #print(booking_result)
            

            results = booking_result
            return results

    def main(self):
        self.user_data = self.db_manager.fetch_all_users()
        #将元组转换为json格式，以users为键
        self.user_data = {"users": [dict(zip([column[0] for column in self.db_manager.cursor.description], row)) for row in self.user_data]}
        print(self.user_data)
        results = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.if_book, user) for user in self.user_data["users"]]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    results.append(result)

        return results


# 主函数
def updatedb():
    db_manager = DatabaseManager()

    try:
        reservation = SeatReservation(db_manager)
        result = reservation.main()
        print(result)

        # 更新用户数据
        for user in result:
            db_manager.update_user(user)

    finally:
        db_manager.close()
    return "ok"