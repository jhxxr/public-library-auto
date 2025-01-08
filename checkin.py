import requests
import json
import returnkey
import pymysql
from datetime import datetime, timedelta
import concurrent.futures
import time
import random
import ssl
import os
import pushwx
all_success = True

mytoken = ''#扫描二维码获取的token

# # SSL CA证书内容（这里以省略形式展示，您需要将证书内容完整复制到这个长字符串中）(一般不用)
# ca_cert = """
# -----BEGIN CERTIFICATE-----
# -----END CERTIFICATE-----

# """

# # 使用字符串创建SSL上下文
# ssl_ctx = ssl.create_default_context(cafile=None, capath=None, cadata=ca_cert)

# # 设置SSL上下文以供后续连接使用
# ssl_params = {'ssl': ssl_ctx}

class DatabaseManager:
    def __init__(self):

        # 在初始化时连接数据库
        self.conn = pymysql.connect(
            # host='',
            # port=4000,
            # user='',
            # password='',
            # db='',
            # ssl=ssl_params  # 使用SSL参数 一般不用
        )

        # 创建游标
        self.cursor = self.conn.cursor()

    def get_users_for_checkin(self):
        # 获取当前时间
        current_time = datetime.now()
        print(current_time)
        
        # 构建字典列表，包含需要签到的用户信息
        users_for_checkin = []

        # 查询整个users表的用户
        sql = "SELECT name, account, password, startTime, endTime, status, bookid FROM users"
        self.cursor.execute(sql)

        # 获取所有数据
        rows = self.cursor.fetchall()

        for row in rows:
            user_start_time = row[3]
            print(row[0], user_start_time)
            
            # 计算用户的签到时间范围
            checkin_start_time = datetime.combine(current_time.date(), datetime.min.time()) + timedelta(hours=user_start_time-0.5)
            checkin_end_time = datetime.combine(current_time.date(), datetime.min.time()) + timedelta(hours=user_start_time, minutes=15)
            # 假设现在是上午8点31分
            #current_time = datetime(2024, 3, 26, 8, 31)

            # 如果当前时间在签到时间范围内，则添加到列表
            
            if checkin_start_time <= current_time <= checkin_end_time:
                if row[5] == "未签到":
                    user_dict = {
                        "name": row[0],
                        "account": row[1],
                        "password": row[2],
                        "startTime": row[3],
                        "endTime": row[4],
                        "bookid": row[6]
                    }
                    users_for_checkin.append(user_dict)

        # 返回需要签到的用户列表
        print(users_for_checkin)
        return users_for_checkin

    
    def close(self):
        # 关闭游标和数据库连接
        self.cursor.close()
        self.conn.close()

def check_in(user_token,bookid,md5):
    sleep_time = random.uniform(0, 2)
    time.sleep(sleep_time)
    key = returnkey.xcode("GET")
    X_request_id = key[0]
    X_request_date = key[1]
    X_hmac_request_key = key[2]
    url = f"https://leosys.cn/cczukaoyan/rest/v2/checkInByQr/{bookid}?md5Str={md5}"
    headers = {
        "content-type": "application/json",
        "X-request-id": X_request_id,
        "Connection": "keep-alive",
        "X-hmac-request-key": X_hmac_request_key,
        "Accept-Encoding": "gzip,compress,br,deflate",
        "User-Agent": "Mozilla/5.0 (iPad; CPU OS 17_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.47(0x18002f2b) NetType/WIFI Language/zh_CN",
        "token": user_token,
        "loginType": "APPLET",
        "user_ip": "58.241.81.202",
        "Host": "leosys.cn",
        "X-request-date": X_request_date,
        "Referer": "https://servicewechat.com/wx8adafd853fc21fd6/86/page-frame.html"
    }
    try:
        response = requests.get(url, headers=headers)
        #{"status":"fail","data":null,"message":"请扫描选座机屏幕上动态二维码，重新扫描","code":"1"}
        response.raise_for_status()
        res = response.json()
        if res["status"] == "fail":
            print(res["message"])
            return {
                "status": "error",
                "message": res["message"]
            }
        else:
            print("签到成功")
            return {
                "status": "success",
                "message": "签到成功"
            }

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return {
            "status": "error",
            "message": "请求错误"
        }
def login(username, password):
        random_delay = random.uniform(0.2, 2)
        time.sleep(random_delay)#随机延时
        logi = f'https://leosys.cn/cczukaoyan/rest/auth?username={username}&password={password}'
        key = returnkey.xcode("GET")
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


        max_login_attempts = 3
        for attempt in range(max_login_attempts):
            try:
                response = requests.get(logi, headers=headers)
                raw_json = response.json()  # Attempt to decode JSON from the response

                if raw_json['status'] == 'success' and 'token' in raw_json['data']:
                    # Successful login
                    token = raw_json['data']['token']
                    print(f"用户 {username} 登录成功")
                    return token
                else:
                    # Failed login or other errors
                    error_message = raw_json.get('message', '未知错误')
                    print(f"登录失败: {error_message}, 将在1秒后重试...")
                    time.sleep(1)
                    continue

            except requests.RequestException as e:
                # Handle request errors
                if attempt < max_login_attempts - 1:
                    print(f"网络异常或请求错误: {e}, 正在重试...")
                    time.sleep(1)
                    continue
                else:
                    print(f"登录失败，请求异常: {e}")
                    return None
            except json.JSONDecodeError as e:
                # Handle invalid JSON decoding
                if attempt < max_login_attempts - 1:
                    print(f"响应不包含有效的JSON: {e}, 正在重试...")
                    time.sleep(1)
                    continue
                else:
                    print(f"登录失败，响应不包含有效的JSON: {e}")
                    return None

        return None # Return None if login was not successful

def user_check_in(user, md5):
    result = {"name": user['name'], "status": "", "message": "", "bookid": user['bookid']}
    try:
        token = login(user['account'], user['password'])
        if 'error' in token:
            result['status'] = "error"
            result['message'] = token['error']
        else:
            yuyueid = result['bookid']
            if yuyueid == 0:
                result['status'] = "error"
                result['message'] = "没有预约"
            elif yuyueid == -1:
                result['status'] = "error"
                result['message'] = "已签到"
            else:
                print(f"用户 {user['name']} 可以签到")
                res = check_in(token, yuyueid, md5)
                result['status'] = res['status']
                result['message'] = res['message']
        return result
    except Exception as e:
        result['status'] = "error"
        result['message'] = f"签到异常: {str(e)}"
        return result

def check_in_auto(md5):
    check_in_results = []
    db_manager = DatabaseManager()
    try:
        users_to_check_in = db_manager.get_users_for_checkin()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # 使用 map 替代列表推导式和 as_completed 方式
            results = executor.map(user_check_in, users_to_check_in, [md5]*len(users_to_check_in))

            # 收集每个用户的签到结果
            for result in results:
                check_in_results.append(result)

    finally:
        db_manager.close()

    # 打印或返回所有用户签到结果
    for result in check_in_results:
        if result['status'] != 'success':
            all_success = False
        print(f"用户 {result['name']} 签到状态: {result['status']}, 消息: {result['message']}")
        pushwx.send_wxpusher_message(f"签到 {result['name']} : {result['status']}", f"消息: {result['message']}")
    if check_in_results == []:
        check_in_results == [{"status":"success"}]
    os.environ['signstatus'] = str(check_in_results)

    return check_in_results

check_in_auto(mytoken)
