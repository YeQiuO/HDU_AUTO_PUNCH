import os
import sys
import time

import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class Punch:

    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(service=Service('/usr/bin/chromedriver'), options=chrome_options)
        self.wait = WebDriverWait(self.driver, 3, 0.5)

    # 获取本地 SESSIONID
    def login(self):
        browser = self.driver
        un = os.environ["SCHOOL_ID"].strip()  # 学号
        pd = os.environ["PASSWORD"].strip()  # 密码

        try:
            print(self.driver)
            browser.get("https://cas.hdu.edu.cn/cas/login")
            print(self.driver)
            self.wait.until(EC.presence_of_element_located((By.ID, "un")))
            self.wait.until(EC.presence_of_element_located((By.ID, "pd")))
            self.wait.until(EC.presence_of_element_located((By.ID, "index_login_btn")))
            browser.find_element(By.ID, 'un').clear()
            browser.find_element(By.ID, 'un').send_keys(un)  # 传送帐号
            browser.find_element(By.ID, 'pd').clear()
            browser.find_element(By.ID, 'pd').send_keys(pd)  # 输入密码
            browser.find_element(By.ID, 'index_login_btn').click()
        except Exception as e:
            print(e.__class__.__name__ + "无法访问数字杭电")
            self.wechatNotice(os.environ["SCKEY"], "无法访问数字杭电")
            sys.exit(1)

        try:
            self.wait.until(EC.presence_of_element_located((By.ID, "errormsg")))
            print("帐号登录失败")
            self.wechatNotice(os.environ["SCKEY"], un + "帐号登录失败")
        except TimeoutException as e:
            browser.get("https://skl.hduhelp.com/passcard.html#/passcard")
            for retryCnt in range(10):
                time.sleep(1)
                sessionId = browser.execute_script("return window.localStorage.getItem('sessionId')")
                if sessionId is not None and sessionId != '':
                    break
            print(self.send(sessionId))
        finally:
            browser.quit()

    # 执行打卡
    def send(self, sessionid):
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
                elif retryCnt == 3:
                    print("提交表单失败")
                    self.wechatNotice(os.environ["SCKEY"], "打卡失败")
            except Exception as e:
                if retryCnt < 2:
                    print(e.__class__.__name__ + "打卡失败，正在重试")
                    time.sleep(3)
                else:
                    print("打卡失败")
                    self.wechatNotice(os.environ["SCKEY"], "打卡失败")

    # 打卡失败微信提示
    def wechatNotice(self, SCKey, message):
        if os.environ["SCKEY"] != '':
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
    punch = Punch()
    punch.login()
