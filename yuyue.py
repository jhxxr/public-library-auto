# -*- coding: utf8 -*-
# 写成接口形式
# 修复之前复用X_request_date的问题
import json
import datetime
import requests
import concurrent.futures
import time
import returnkey
import random
class SeatReservation:
    def __init__(self, user_data):
        self.user_data = user_data
        self.today = datetime.date.today()
        self.tomorrow = self.today + datetime.timedelta(days=1)
        self.user_token = None
        
    def login(self, username, password):
        max_login_attempts = 3
        for attempt in range(max_login_attempts):
            # 获取新的请求键值
            key = returnkey.xcode("GET")
            random_delay = random.uniform(0.5, 2)
            time.sleep(random_delay)#随机延时
            X_request_id = key[0]
            X_request_date = key[1]
            X_hmac_request_key = key[2]
            

            # 构建登录的URL
            logi = f'https://leosys.cn/cczukaoyan/rest/auth?username={username}&password={password}'

            # 配置请求头
            headers = {
                'Host': 'leosys.cn',
                'X-request-date': X_request_date,
                'loginType': 'APPLET',
                'User-Agent': '...',
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
                'Referer': '...',
                'Accept-Language': 'zh-CN,zh;q=0.9',
            }
            
            # 尝试发送请求并处理响应
            try:
                response = requests.get(logi, headers=headers)
                raw_json = response.json()
                print(raw_json)

                if raw_json['status'] == 'success' and 'token' in raw_json['data']:
                    token = raw_json['data']['token']
                    print(f"用户 {username} 登录成功")
                    return token
                else:
                    error_message = raw_json.get('message', '未知错误')
                    print(f"登录失败: {error_message}, 将在1秒后重试...")
                    time.sleep(1)
                    continue

            except requests.RequestException as e:
                if attempt < max_login_attempts - 1:
                    print(f"网络异常或请求错误: {e}, 正在重试...")
                    time.sleep(1)
                    continue
                else:
                    print(f"登录失败，请求异常: {e}")
                    return None

            # 在json.JSONDecodeError异常处理中添加
            except json.JSONDecodeError as e:
                print(f"响应不包含有效的JSON: {e}, 响应内容为: {response.text}")  # 添加这行来打印原始响应文本
                if attempt < max_login_attempts - 1:
                    print("正在重试...")
                    time.sleep(1)
                    continue
                else:
                    print("登录失败，响应不包含有效的JSON")
                    return None
        return None


    def qiangzuowei(self,username,seat, start_time, end_time):
        max_attempts = 3
        attempt = 0
        while attempt < max_attempts:
            print(f"尝试预约 {username} 第 {attempt + 1} 次")
            authid = ""
            Form_data = {
                "seat": seat,
                "date": str(self.today),
                "startTime": int(start_time)*60,
                "endTime": int(end_time)*60,
                "authid": authid,
            }
            url = "https://leosys.cn/cczukaoyan/rest/v2/freeBook"
            key = returnkey.xcode("POST")
            X_request_id = key[0]
            X_request_date = key[1]
            X_hmac_request_key = key[2]

            headers = {
                "Referer": "https://servicewechat.com/wx8adafd853fc21fd6/24/page-frame.html",
                "content-type": "application/x-www-form-urlencoded",
                "User-Agent": "mozilla/5.0 (iphone; cpu iphone os 5_1_1 like mac os x) applewebkit/534.46 (khtml, like gecko) mobile/9b206 micromessenger/5.0",
                "token": self.user_token,
                "X-request-date": X_request_date,
                "X-hmac-request-key": X_hmac_request_key,
                "X-request-id": X_request_id,



            }
            try:
                content = requests.post(url, data=Form_data, headers=headers)
                raw_json = json.loads(content.text)
                if raw_json['status'] == 'success':
                    print(f"{username} 预约成功")
                    return {
                        "yuyue": {
                            "code": "success",
                            "name": username,
                            "data": raw_json["data"],
                            "mess": raw_json["message"],
                            "error": None
                        }
                    }
                else:
                    print(f"{username} 预约失败, 尝试重新预约")
                    attempt += 1
                    time.sleep(1)
            except Exception as e:
                print(f"{username} 预约时出现异常: {e}")
                attempt += 1
                time.sleep(1)
        
        return {
            "yuyue": {
                "code": "fail",
                "name": username,
                "mess": raw_json["message"],
                "error": "预约失败"
            }
        }
    def login_and_reserve(self):
        user_data = self.user_data
        username = user_data['name']

        # 先尝试登录
        token = self.login(user_data['account'], user_data['password'])
        self.user_token = token
        if token:
            print(f"用户 {username} 登录成功，开始预约。")
            # 成功获取token之后尝试预约座位
            reservation_result = self.qiangzuowei(username, user_data['seat'], user_data['startTime'], user_data['endTime'])
            return reservation_result
        else:
            print(f"用户 {username} 登录失败，无法进行预约。")
            return {"yuyue": {"code": "fail", "name": username, "error": "登录失败"}}
        
# 通知函数
def notify_results(results):
    total = len(results)
    success = sum([not result['yuyue']['error'] for result in results])

    # 构建通知的标题，展示预约总数和成功数
    title = f"[Y2]预约{success}/{total}"

    # 构建通知的内容信息
    details = []
    for result in results:
        if result['yuyue']['error']:
            if 'mess' in result['yuyue']:
                detail = f"\n用户 {result['yuyue']['name']} 预约失败: {result['yuyue']['error']} {result['yuyue']['mess']}"
            else:
                detail = f"\n用户 {result['yuyue']['name']} 预约失败: {result['yuyue']['error']}"
        else:
            detail = f"\n用户 {result['yuyue']['name']} 预约成功: {result['yuyue']['data']} {result['yuyue'].get('mess', '')}"
        
        details.append(detail)

    message = "".join(details)

    # 您可以在这里调用pushwx来发送通知，如下：
    #pushwx.send_wxpusher_message(title, message)
  
    return title + message


def main_handler(event, context):
    with open("user.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    
    filtered_users = [user for user in data['users'] if user.get("auto_book", False)]

    # 使用 ThreadPoolExecutor 处理用户登录与预约
    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_user = {executor.submit(SeatReservation(user).login_and_reserve): user for user in filtered_users}
        for future in concurrent.futures.as_completed(future_to_user):
            result = future.result()
            results.append(result)
    notify_results(results)

main_handler(None, None)