import requests
code = "484009"#网页中获取的激活码  http://202.195.100.14/libseat/#/login
url = f"https://leosys.cn/cczukaoyan/rest/v2/checkActivationCode/{code}"
method = "POST"
headers = {
    "Sec-Fetch-Dest": "empty",
    "X-request-id": "fb3ba852-e4a9-4194-b5ae-4ec3038bf2b2",
    "Connection": "keep-alive",
    "X-hmac-request-key": "92ba9444796204651cc47f2d2738d7449209c07403e01e5b7b6333ef6c95b722",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Content-Type": "application/json",
    "Sec-Fetch-Site": "cross-site",
    "loginType": "APPLET",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 MicroMessenger/6.8.0(0x16080000) NetType/WIFI MiniProgramEnv/Mac MacWechat/WMPF MacWechat/3.8.6(0x13080610) XWEB/1156",
    "token": "",
    "Sec-Fetch-Mode": "cors",
    "user_ip": "1.1.1.1",
    "Host": "leosys.cn",
    "X-request-date": "1710316961184",
    "Referer": "https://servicewechat.com/wx8adafd853fc21fd6/87/page-frame.html",
    "xweb_xhr": "1",
    "Accept": "*/*"
}
body = None

response = requests.request(method, url, headers=headers, data=body)

print(response.status_code)
print("\n")
print(response.text)
