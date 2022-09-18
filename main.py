from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import requests
import os

from selenium.common.exceptions import NoSuchElementException


chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# serverchan函数
def serverchan(sendkey, msg, browser):
    if sendkey == '0':
        pass
    else:
        # serverchan消息推送 https://sctapi.ftqq.com/****************.send?title=messagetitle
        url = "https://sctapi.ftqq.com/" + str(sendkey) + ".send?title=" + str(msg)
        browser.get(url)
        time.sleep(3)
        # 退出窗口
        browser.quit()


# 获取本地 SESSIONID
def daka(sendkey, browser):
    # 相关参数定义
    un = os.environ["SCHOOL_ID"].strip()  # 学号
    pd = os.environ["PASSWORD"].strip()  # 数字杭电密码
    # 访问数字杭电
    browser.get("https://cas.hdu.edu.cn/cas/login")
    # 窗口最大化
    browser.maximize_window()
    time.sleep(2)
    # 登录账户
    browser.find_element_by_id('un').clear()
    browser.find_element_by_id('un').send_keys(un)  # 传送帐号
    browser.find_element_by_id('pd').clear()
    browser.find_element_by_id('pd').send_keys(pd)  # 输入密码
    browser.find_element_by_id('index_login_btn').click()
    time.sleep(3)
    try:
        flag = browser.find_element_by_id('errormsg').is_enabled()
    except NoSuchElementException:
        flag = False
    if flag == True:
        print(un + "帐号登录失败")
        serverchan(sendkey, un + "帐号登录失败")
        browser.quit()  # 帐号登录失败
    else:
        # 访问打卡界面
        browser.get("https://skl.hduhelp.com/passcard.html#/passcard")
        print("正在执行" + un + "操作")
        time.sleep(10)
        sessionId = browser.execute_script("return window.localStorage.getItem('sessionId')")
        print(sessionId)
        # 退出窗口
        browser.quit()
        punch(sessionId)


# 执行打卡
def punch(sessionid):
    headers = {
        'Content-Type': 'application/json',
        'X-Auth-Token': sessionid,
        'User-Agent': 'Mozilla/5.0 (Linux; Android 11; Pixel 4 XL Build/RQ3A.210705.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.106 Mobile Safari/537.36 AliApp(DingTalk/5.1.5) com.alibaba.android.rimet/13534898 Channel/212200 language/zh-CN UT4Aplus/0.2.25 colorScheme/light'
    }
    url = "https://skl.hdu.edu.cn/api/punch"
    data = {
        "currentLocation": "浙江省杭州市钱塘区",
        "city": "杭州市",
        "districtAdcode": "330114",
        "province": "浙江省",
        "district": "钱塘区",
        "healthCode": 0,
        "healthReport": 0,
        "currentLiving": 0,
        "last14days": 0
    }
    r = requests.post(url, json=data, headers=headers, timeout=30)
    if r.status_code == 200:
        print("打卡成功")
    else:
        print("打卡失败")

if __name__ == '__main__':
    # ServerChan发送key，0表示不启用推送
    sendkey = '0'
    browser = webdriver.Chrome('/usr/bin/chromedriver', options=chrome_options)
    daka(sendkey, browser)
    time.sleep(3)
