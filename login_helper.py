"""
这段代码是一个 单点登录工具类，采用单例模式保证全局唯一浏览器和会话。
通过 Selenium 启动无头浏览器 自动完成账号密码输入、登录操作。
登录成功后，提取浏览器的 Cookie，并注入到 requests.Session 中，
实现 UI 登录态共享给接口自动化，让接口可以免登录直接调用，提高自动化执行效率。
"""

import requests
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from typing import Optional  # 类型提示，规范代码
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config.env_config import *
import logging


class SAMLLoginHelper:
    _instance = None
    _driver = None
    _session = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            return cls._instance

    def __int__(self, username: str = None, password: str = None):
        # 防止重复初始化
        if hasattr(self, '_initialized'):
            return self._initialized == True
        self.username = username or ENV_VARS[ENV]['username']
        self.password = password or ENV_VARS[ENV]['password']
        # 确保全局driver和session只初始化一次
        if SAMLLoginHelper._driver is None:
            SAMLLoginHelper._driver = self._start_browser()
        if SAMLLoginHelper._session is None:
            SAMLLoginHelper._session = requests.Session()
            self.driver = SAMLLoginHelper._driver
            self.session = SAMLLoginHelper._session

    def _start_browser(self):
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--headless')  # 无头模式，后台静默运行
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        driver_path = os.path.join(project_root, "drivers", "chromedriver-win64", "chromedriver.exe")
        if not os.path.exists(driver_path):
            raise FileNotFoundError(f"未找到chromedriver.exe,路径:{driver_path}")
        logging.info(f"使用本地chromedriver:{driver_path}")
        return webdriver.Chrome(executable_path=driver_path, options=chrome_options)

    def login(self, login_url):
        if not self.driver:
            self.driver = self._start_browser()
            self.driver.get(login_url)
            logging.info(f"正在访问登录页:{login_url}")
            # 等待登录也加载完成
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(("id", "username")))
            # 输入用户名和密码
            self.driver.find_element("id", "username").send_keys(self.username)
            self.driver.find_element("id", "password").clear()
            self.driver.find_element("id", "password").send_keys(self.password)
            # 点击登录
            self.driver.find_element("id", "w3-login-button").click()
            logging.info("正在登录中...")
            # 等待跳转完成（替换time.sleep）
        try:
            # 根据实际跳转地址调整
            WebDriverWait(self.driver, 15).until(EC.url_contains(ENV_VARS[ENV]["project_url"]))
        except:
            logging.info("登录跳转超时，尝试继续...")
            time.sleep(3)
            # 获取location.hash：前端里用来获取 / 设置 URL 中 # 后面部分的属性
            hash_value = self.driver.execute_script("return window.location.hash;")
            logging.info(f"获取到location.hash:{hash_value}")
            # 提取Cookies并注入到session
            cookies = self.driver.get_cookies()  # 获取浏览器登录后的所有Cookie
            # 遍历每一条Cookie
            for cookie in cookies:
                # 把Cookie设置到requests的session里
                self.session.cookies.set(cookie['name'], cookie['value'], domain=cookie.get('domain', ))
            logging.info("登录成功,Session已更新")
            return self.session

    @classmethod
    def get_instance(cls, *args, **kwargs):
        return cls(*args, **kwargs)

    @classmethod
    def close(cls):
        if cls._driver:
            cls._driver.quit()
            cls._driver = None
            logging.info("浏览器已关闭")
