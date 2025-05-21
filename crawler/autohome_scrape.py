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

from autohome_utils import *

chrome_options = Options()
chrome_options.add_argument('--disable-plugins-discovery')
chrome_options.add_argument('--mute-audio')
# chrome_options.add_argument('--headless')
chrome_options.add_argument("--disable-plugins-discovery")
chrome_options.add_argument("--mute-audio")
chrome_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument("--disable-infobars") 
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36 Edg/89.0.774.77")


cookies_file = 'crawler/autohome_cookies.pkl'
user_profile_url = 'https://i.autohome.com.cn/289936713'


def get_post_detail_links(driver, url, page_num, time_out=10):
    
    links = []
    try:
        driver.get(url)
        
        wait = WebDriverWait(driver, time_out)
        
        # 等待页面基本元素加载完成
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        scroll_to_bottom(driver)
        
        max_retries = 3
        retries = 0
        while retries < max_retries:
            try:
                print(f"Getting links for page {page_num}...")
                
                linkListItems = wait.until(EC.presence_of_all_elements_located(
                    (By.XPATH, "//ul[contains(@class, 'post-list')]/li[not(contains(@class, 'video-type'))]")))

                for listItem in linkListItems:
                    aElement = listItem.find_element(By.XPATH, ".//p[contains(@class, 'post-title')]/a")
                    href = aElement.get_attribute("href")
                    links.append(href)
                break

            except Exception as e:
                print(f"Attempt {retries+1} for page {page_num} failed: \n{e}")
                time.sleep(2)
                scroll_to_bottom(driver, 1)  # 重试时再次滚动
                continue
                
            finally:
                retries += 1

        else:
            print("Failed to retrieve content with all selectors.")
            
    except Exception as e:
        print(f'Failed to get posts from page {page_num}:\n{e}')
        if driver:
            save_error_page(driver, url)

    finally:
        return links


def get_post_detail(driver, url, time_out=10):
    
    driver.get(url)
    
    wait = WebDriverWait(driver, time_out)
    
    # 等待页面基本元素加载完成
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    
    scroll_to_bottom(driver)
    
    max_retries = 3
    retries = 0
    while retries < max_retries:
        try:    
            usernameElement = driver.find_elements(By.CSS_SELECTOR, ".user-name")
            if len(usernameElement)>0:
                username = usernameElement[0].text
            else:
                username = 'Empty'

            timestampElement = driver.find_elements(By.CSS_SELECTOR, ".post-handle-publish")
            if len(timestampElement)>0:
                timestamp_str = timestampElement[0].text
                timestamp = to_timestamp(timestamp_str)
            else:
                return None

            titleElement = driver.find_elements(By.CSS_SELECTOR, ".post-title")
            if len(titleElement)>0:
                title = titleElement[0].text.strip()
            else:
                title = ''

            contentElements = driver.find_elements(By.CSS_SELECTOR, ".tz-paragraph")
            
            if len(contentElements) > 0:
                content = title + '\n' + '\n'.join([contentElement.text.strip() for contentElement in contentElements])
                
                reply_elems = driver.find_elements(By.CSS_SELECTOR, ".reply-detail")
                reply_time_elems = driver.find_elements(By.CSS_SELECTOR, ".reply-static-text.fn-fl:not(.fn-hide)")
                
                replyies = []
                for reply_elem, reply_time_elem in zip(reply_elems, reply_time_elems):
                    reply_content = reply_elem.text.strip()
                    reply_time_str = reply_time_elem.text.strip()
                    reply_time = to_timestamp(reply_time_str)
                    replyies.append({
                        "content": reply_content,
                        "timestamp": reply_time
                    })
                    
                post = {
                    'url': url,
                    "timestamp": timestamp,
                    "username": username,
                    "content": content,
                    "replies": replyies
                    }
                return post
            
            else:
                print("No content found.")
                return None
                
        except Exception as e:
            print(f"Attempt {retries+1} for {url} failed: \n{e}")
            time.sleep(2)
            scroll_to_bottom(driver, 1)  # 重试时再次滚动
            continue
            
        finally:
            retries += 1
            
    else:
        print("Failed to retrieve content with all selectors.")
        # 保存错误页面源码
        save_error_page(driver, url)
        return None
            

def scrape_posts(product_name, url, totalPages, offset=0):
    links = []
    posts = []
    
    get_cookies(user_profile_url, cookies_file)
    
    # driver = webdriver.Chrome(options=chrome_options)
    service = Service('crawler/chromedriver-win64/chromedriver.exe') # 请下载对应版本的chromedriver 或者替换为service = Service(ChromeDriverManager(url="https://registry.npmmirror.com/-/binary/chromedriver").install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(user_profile_url)
    load_cookies(driver, cookies_file)

    driver.set_window_size(1920, 1080)
    
    for i in range(0, totalPages):

        formatted_url = url.format(page_num=i+offset+1)
        partial_links = get_post_detail_links(driver, formatted_url, i+1)
        tmp = {
            "page_num": i+1+offset,
            "links": partial_links
        }
        links.append(tmp)
    
    link_count = sum([len(dict['links']) for dict in links])
    
    for dict in links:
        page_num = dict['page_num']

        for idx, link in enumerate(dict['links']):
            print(f'Scraping post {idx+1}/{link_count} of page {page_num} for {product_name}')
            post = get_post_detail(driver, link, page_num)
            
            if post:
                posts.append(post)
    driver.quit()
    return posts

__all__ = ['scrape_posts']

# def main():
#     start_time = time.perf_counter()
    
#     tasks = [
#         # {'name':'lixiang_l6', 'totalPages':51, 'offset':0, 'url':'https://club.autohome.com.cn/bbs/forum-c-6950-{page_num}.html#pvareaid=3454448'},
#         # {'name':'yinhe_E8', 'totalPages':65, 'offset':0, 'url':'https://club.autohome.com.cn/bbs/forum-c-7170-{page_num}.html#pvareaid=6830272'},
#         # {'name':'byd_han', 'totalPages':200, 'offset':0, 'url':'https://club.autohome.com.cn/bbs/forum-c-5499-{page_num}.html#pvareaid=3454448'},
#         {'name':'lynk_900', 'totalPages':20, 'offset':0, 'url':'https://club.autohome.com.cn/bbs/forum-c-8002-{page_num}.html'}
#     ]
    
#     for task in tasks:
#         posts = scrape_posts(product_name=task['name'], url=task['url'] ,totalPages=task['totalPages'], offset=task['offset'])
    
#         with open(f'{task["name"]}.json', 'w', encoding='utf-8') as f:
#             json.dump(posts, f, ensure_ascii=False, indent=4)

#     end_time = time.perf_counter()
#     print(f'Total time cost: {round(end_time - start_time)} seconds')

def main():
    start_time = time.perf_counter()
    
    get_cookies(user_profile_url, cookies_file)
    
    # driver = webdriver.Chrome(options=chrome_options)
    service = Service('crawler/chromedriver-win64/chromedriver.exe') # 请下载对应版本的chromedriver 或者替换为service = Service(ChromeDriverManager(url="https://registry.npmmirror.com/-/binary/chromedriver").install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(user_profile_url)
    load_cookies(driver, cookies_file)

    driver.set_window_size(1920, 1080)
    
    links = read_json("crawler/autohome_links.json")
    progress = read_json("crawler/autohome_progress.json")
    results = {}
    for product_name, links in links.items():
        if not results.get(product_name, None):
            results[product_name] = []
            
        if product_name != 'lynk_900':
            continue

        for link in links:
            if link in progress:
                continue
            print(f'Scraping post {link} for {product_name}')
            post = get_post_detail(driver, link, 1)

            if post:
                results[product_name].append(post)
                progress.append(link)
                write_json(results, "crawler/autohome_posts.json")
                write_json(progress, "crawler/autohome_progress.json")
                
            time.sleep(random.uniform(1, 3))  # 避免请求过于频繁，也可以根据需要调整时间间隔
            
    
    driver.quit()

    end_time = time.perf_counter()
    print(f'Total time cost: {round(end_time - start_time)} seconds')
    
if __name__ == "__main__":
    main()
    