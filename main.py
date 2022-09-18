import os
import time

import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')


# 打卡失败微信提示
def wechatNotice(SCKey, message):
    print(message)
    url = 'https://sctapi.ftqq.com/{0}.send'.format(SCKey)
    print(url)
    data = {
        'title': message,
    }
    try:
        r = requests.post(url, data=data)
        if r.json()["data"]["error"] == 'SUCCESS':
            print("微信通知成功")
        else:
            print("微信通知失败")
    except Exception as e:
        print(e.__class__, "推送服务配置错误")


# 获取本地 SESSIONID
def daka(sendkey, browser):
    # 相关参数定义
    un = os.environ["SCHOOL_ID"].strip()  # 学号
    pd = os.environ["PASSWORD"].strip()  # 数字杭电密码
    # 访问数字杭电
    browser.get("https://cas.hdu.edu.cn/cas/login")
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

    if flag:
        print(un + "帐号登录失败")
        if os.environ["SCKEY"] != '':
            wechatNotice(os.environ["SCKEY"], un + "帐号登录失败")
        browser.quit()
    else:
        # 获取 sessionId
        browser.get("https://skl.hduhelp.com/passcard.html#/passcard")
        time.sleep(10)
        sessionId = browser.execute_script("return window.localStorage.getItem('sessionId')")
        browser.quit()

        # 调用打卡接口
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
        wechatNotice(os.environ["SCKEY"], "打卡失败")


if __name__ == '__main__':
    daka(webdriver.Chrome('/usr/bin/chromedriver', options=chrome_options))
