import os
import time

import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')


# 执行打卡
def send(sessionid):
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

    for retryCnt in range(3):
        try:
            res = requests.post(url, json=data, headers=headers, timeout=30)
            if res.status_code == 200:
                return "打卡成功"
            else:
                print("打卡失败")
                wechatNotice(os.environ["SCKEY"], "打卡失败")
        except Exception as e:
            print(e.__class__.__name__, end='\t')
            if retryCnt < 2:
                print("打卡失败，正在重试")
                time.sleep(3)
            else:
                print("打卡失败")
                wechatNotice(os.environ["SCKEY"], "打卡失败")


# 获取本地 SESSIONID
def punch(browser, wait):
    # 相关参数定义
    un = os.environ["SCHOOL_ID"].strip()  # 学号
    pd = os.environ["PASSWORD"].strip()  # 密码

    try:
        browser.get("https://cas.hdu.edu.cn/cas/login")
        wait.until(EC.presence_of_element_located((By.ID, "un")))
        wait.until(EC.presence_of_element_located((By.ID, "pd")))
        wait.until(EC.presence_of_element_located((By.ID, "index_login_btn")))
        browser.find_element(By.ID, 'un').clear()
        browser.find_element(By.ID, 'un').send_keys(un)  # 传送帐号
        browser.find_element(By.ID, 'pd').clear()
        browser.find_element(By.ID, 'pd').send_keys(pd)  # 输入密码
        browser.find_element(By.ID, 'index_login_btn').click()
        wait.until(EC.presence_of_element_located((By.ID, "errormsg")))
    except TimeoutException as e:
        browser.get("https://skl.hduhelp.com/passcard.html#/passcard")
        for retryCnt in range(10):
            time.sleep(1)
            sessionId = browser.execute_script("return window.localStorage.getItem('sessionId')")
            if sessionId is not None and sessionId != '':
                break
        print(send(sessionId))
    except Exception as e:
        print(e.__class__.__name__ + "帐号登录失败")
        if os.environ["SCKEY"] != '':
            wechatNotice(os.environ["SCKEY"], un + "帐号登录失败")

    browser.quit()


# 打卡失败微信提示
def wechatNotice(SCKey, message):
    url = 'https://sctapi.ftqq.com/{0}.send'.format(SCKey)
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


if __name__ == '__main__':
    driver = webdriver.Chrome(service=Service('/usr/bin/chromedriver'), options=chrome_options)
    wait = WebDriverWait(driver, 3, 0.5)

    punch(driver, wait)
