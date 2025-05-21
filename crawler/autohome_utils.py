import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import csv
import time
import os
import random
import pickle
    
from datetime import datetime, timedelta
import re


def get_cookies(user_profile_url, cookies_file):
    # 首次登录获取cookie文件
    print("测试cookies文件是否已获取。若无，请在弹出的窗口使用账户密码登录")

    login_chrome_options = Options()
    login_chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=login_chrome_options)
    
    driver.get(user_profile_url)
    
    if not load_cookies(driver, cookies_file):
        manual_login(driver, cookies_file)
    driver.quit()

def save_error_page(driver, url):
    """保存错误页面源码的辅助函数"""
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        url_div = soup.new_tag("div", style="font-weight: bold; margin-bottom: 20px;")
        url_div.string = f"Page URL: {url}"
        
        if soup.body:
            soup.body.insert(0, url_div)
        else:
            soup.append(url_div)
            
        filename_base = url.rsplit('/', 1)[-1]
        output_folder = "error_pages"
        os.makedirs(output_folder, exist_ok=True)
        
        file_path = os.path.join(output_folder, f'page_source_{filename_base}.html')
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(soup.prettify()) # type: ignore
            
    except Exception as e:
        print(f"Failed to save error page: {e}")

         
def scroll_to_bottom(driver, wait_time=1):
    """渐进式滚动到页面底部，模拟真实用户行为"""
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        # 滚动一小段距离
        for i in range(3):
            current_height = last_height // 3 * (i + 1)
            driver.execute_script(f"window.scrollTo(0, {current_height});")
            time.sleep(random.uniform(0.5, 1))
            
        # 等待页面加载
        # time.sleep(wait_time)
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        

def save_cookies(driver, cookies_file):
    with open(cookies_file, 'wb') as f:
        pickle.dump(driver.get_cookies(), f)

def load_cookies(driver, cookies_file):
    if os.path.exists(cookies_file):
        with open(cookies_file, 'rb') as f:
            cookies = pickle.load(f)
        for cookie in cookies:
            driver.add_cookie(cookie)
        return True
    return False

def manual_login(driver, cookies_file):
    input("请登录，登录成功跳转后，按回车键继续...")
    save_cookies(driver, cookies_file)  # 登录后保存cookie到本地
    print("程序正在继续运行")
    

def read_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        raise
    
def write_json(data, file_path):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except IOError as e:
        print(f"Error writing to file: {e}")
        raise


def to_timestamp(time_str):
    # 匹配 "x小时前"，不限定位置，取最后一个匹配项
    hour_matches = list(re.finditer(r'(\d+)小时前', time_str))
    if hour_matches:
        hours_ago = int(hour_matches[-1].group(1))  # 取最后一个匹配
        return int((datetime.now() - timedelta(hours=hours_ago)).timestamp())

    # 匹配 "x天前"
    day_matches = list(re.finditer(r'(\d+)天前', time_str))
    if day_matches:
        days_ago = int(day_matches[-1].group(1))
        return int((datetime.now() - timedelta(days=days_ago)).timestamp())

    # 匹配标准时间格式 yyyy-mm-dd hh:mm:ss（必须出现在字符串结尾）
    date_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})$', time_str)
    if date_match:
        dt_str = date_match.group(1)
        try:
            dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            return int(dt.timestamp())
        except ValueError:
            pass  # 如果转换失败，则继续到下一步

    # 都不匹配则返回原字符串
    return time_str

if __name__ == "__main__":
    print(to_timestamp("3小时前"))         # 输出当前时间减去3小时的时间戳
    print(to_timestamp("2天前"))            # 输出当前时间减去2天的时间戳
    print(to_timestamp("发布于 湖北 2025-03-26 16:50:37"))  # 输出对应的时间戳
    print(to_timestamp("invalid string"))  # 输出: invalid string