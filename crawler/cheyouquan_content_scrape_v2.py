import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import time
import os
import random
import pickle

chrome_options = Options()
chrome_options.add_argument('--disable-plugins-discovery')
chrome_options.add_argument('--mute-audio')
# chrome_options.add_argument('--headless')
chrome_options.add_argument("--disable-plugins-discovery")
chrome_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument("--disable-infobars") 


cookies_file = 'crawler/dongchedi_cookies.pkl'
user_profile_url = 'https://www.dongchedi.com/user/1088957342821306'

from datetime import datetime, timedelta
import re

def parse_time_string(time_str):
    # 去除结尾的“回复”
    time_str = time_str.strip().rstrip("回复").strip()

    now = datetime.now()

    # 匹配 "刚刚"
    if time_str == "刚刚":
        return int((now - timedelta(minutes=1)).timestamp())

    # 匹配 x分钟前
    minute_match = re.search(r'(\d+)分钟前', time_str)
    if minute_match:
        minutes_ago = int(minute_match.group(1))
        return int((now - timedelta(minutes=minutes_ago)).timestamp())

    # 匹配 x小时前
    hour_match = re.search(r'(\d+)小时前', time_str)
    if hour_match:
        hours_ago = int(hour_match.group(1))
        return int((now - timedelta(hours=hours_ago)).timestamp())

    # 匹配 昨天 hh:mm
    yesterday_match = re.search(r'昨天 (\d{2}:\d{2})', time_str)
    if yesterday_match:
        hour, minute = map(int, yesterday_match.group(1).split(':'))
        yesterday = (now - timedelta(days=1)).replace(hour=hour, minute=minute, second=0, microsecond=0)
        return int(yesterday.timestamp())

    # 匹配 前天 hh:mm
    day_before_yesterday_match = re.search(r'前天 (\d{2}:\d{2})', time_str)
    if day_before_yesterday_match:
        hour, minute = map(int, day_before_yesterday_match.group(1).split(':'))
        day_before = (now - timedelta(days=2)).replace(hour=hour, minute=minute, second=0, microsecond=0)
        return int(day_before.timestamp())

    # 匹配 x天前
    day_match = re.search(r'(\d+)天前', time_str)
    if day_match:
        days_ago = int(day_match.group(1))
        return int((now - timedelta(days=days_ago)).timestamp())

    # 匹配 mm-dd
    md_match = re.search(r'(\d{2})-(\d{2})', time_str)
    if md_match:
        month, day = map(int, md_match.groups())
        try:
            dt = now.replace(month=month, day=day, hour=0, minute=0, second=0, microsecond=0)
            # 如果日期比现在还大（比如12月解析成当前年份的1月），则自动减一年
            if dt > now:
                dt = dt.replace(year=dt.year - 1)
            return int(dt.timestamp())
        except ValueError:
            pass  # 比如 02-30 是非法日期

    # 匹配 yyyy-mm-dd
    ymd_match = re.search(r'(\d{4}-\d{2}-\d{2})', time_str)
    if ymd_match:
        try:
            dt = datetime.strptime(ymd_match.group(1), "%Y-%m-%d")
            return int(dt.timestamp())
        except ValueError:
            pass

    # 匹配 yyyy-mm-dd HH:MM:SS
    ymdhms_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', time_str)
    if ymdhms_match:
        try:
            dt = datetime.strptime(ymdhms_match.group(1), "%Y-%m-%d %H:%M:%S")
            return int(dt.timestamp())
        except ValueError:
            pass

    # 都不匹配就返回原字符串
    return time_str


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

def scroll_to_bottom(driver, wait_time=2):
    """渐进式滚动到页面底部，模拟真实用户行为"""
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        # 滚动一小段距离
        for i in range(3):
            current_height = last_height // 3 * (i + 1)
            driver.execute_script(f"window.scrollTo(0, {current_height});")
            time.sleep(random.uniform(0.5, 1))
            
        # 等待页面加载
        time.sleep(wait_time)
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def get_posts_by_page(driver, url, page_num, time_out=15):
    
    url = f"{url}/{page_num}"
    posts = []

    try:
        driver.get(url)
        wait = WebDriverWait(driver, time_out)
        print(f"Getting page {page_num}...")
        
        # 等待页面基本元素加载完成
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # 执行渐进式滚动
        scroll_to_bottom(driver)
        
        print(f"Getting content for page {page_num}...")
        
        spanElements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".jsx-81802501.jsx-2089696349.tw-text-common-black")))
        usernameElements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".tw-text-16.tw-text-black")))
        linkElements = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//section/div/p/a")))
        timestampElements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".jsx-1875074220.tw-text-video-shallow-gray.tw-flex-none")))
        
        links = []
        if linkElements:
            for aElement in linkElements:
                href = aElement.get_attribute("href")
                if href is not None and 'ugc/article' in href:
                    links.append(href)
        
        if spanElements and usernameElements and links and timestampElements:
            for spanElement, usernameElement, link, timestampElement in zip(spanElements, usernameElements, links, timestampElements):
                if spanElement.text.strip() == '':
                    continue

                post = {
                    'url': link,
                    "timestamp": parse_time_string(timestampElement.text) or '无时间戳',
                    "username": usernameElement.text or '无用户名',
                    "content": spanElement.text.strip(),
                    "replies": []
                    }
                posts.append(post)
         
    except Exception as e:
        print(f'Failed to get posts from page {page_num}:\n{e}')

    finally:
        return posts

def main():
    # 首次登录获取cookie文件
    print("测试cookies文件是否已获取。若无，请在弹出的窗口中登录，登录完成后，窗口将关闭；若有，窗口会立即关闭")
    driver = webdriver.Chrome(service=Service(executable_path=ChromeDriverManager().install()))
    driver.get(user_profile_url)
    if not load_cookies(driver, cookies_file):
        manual_login(driver, cookies_file)

    start_time = time.perf_counter()

    url = 'https://www.dongchedi.com/community/6095'

    totalPages = 121
    offset = 150

    driver.set_window_size(1920, 1080)
        
    with open('crawler/dongchedi_posts.json', 'r', encoding='utf-8') as file:
        results = json.load(file)
    
    for i in range(totalPages):
        posts = get_posts_by_page(driver, url, i+offset+1)
        results["lixiang_l8"].extend(posts)
        time.sleep(random.uniform(1, 5))
    
    with open('crawler/dongchedi_posts.json', 'w', encoding='utf-8') as file:
        json.dump(results, file, ensure_ascii=False, indent=4)
        
    end_time = time.perf_counter()
    print(f'Total time cost: {round(end_time - start_time)} seconds')

if __name__ == "__main__":
    main()