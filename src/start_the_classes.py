import re
import time
import threading
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from colorama import Fore, init
init(autoreset=True)

from utils import create_driver

semaphore = threading.Semaphore(4) # control the number of concurrent video playbacks

def check_current_dom(elem):
    parent = elem.find_element(By.XPATH, '..')  # 取得父節點
    print(parent.get_attribute('outerHTML'))

    siblings = elem.find_elements(By.XPATH, 'following-sibling::*')
    for s in siblings:
        print(s.get_attribute('outerHTML'))



def start_class(course_url):
    print(Fore.WHITE + "[Info] " + "="*10 + " Start fetching video links " + "="*10)
    driver = create_driver()
    driver.get(course_url)
    video_list = []

    # 等待影片區塊出現
    time.sleep(3)
    video_blocks = WebDriverWait(driver, 60).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.center-part > span.xtree-node-label"))
    )
    print(Fore.YELLOW + f"[Warning] Found {len(video_blocks)} video blocks")

    for block in video_blocks:
        print(Fore.MAGENTA + "[Info] Waiting for video link to load...")
        WebDriverWait(block, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".fs-singleLineText a[href^='/media/']"))
        )
        check_current_dom(block)
        # 抓標題
        try:
            title_elem = block.find_element(By.CSS_SELECTOR, '.node-title')
            title = title_elem.text.strip()
        except NoSuchElementException:
            title = "Unknown Title"
        print(Fore.BLUE + f"Processing video: {title}")

        # 抓連結
        try:
            link_elem = block.find_element(By.CSS_SELECTOR, '.node-title a[href^="/media/"]')
            href = link_elem.get_attribute("href")
        except NoSuchElementException:
            href = None
            print(Fore.RED + f"[Danger] No href found for {title}, skip")
            exit(1)
            continue  # 跳過這個影片

        # 抓時間（同一個父節點的兄弟元素）
        try:
            time_elem = block.find_element(By.CSS_SELECTOR, '.hidden-xs.pull-right .col-char7')
            time_text = time_elem.text.strip()
            if "分鐘" in time_text:
                minutes = int(re.search(r'\d+', time_text).group())
            elif "次" in time_text:
                times = int(re.search(r'\d+', time_text).group())
                minutes = times * 5
            else:
                minutes = 5
        except NoSuchElementException:
            minutes = 5
            print(Fore.YELLOW + f"[Warning] No time info for {title}, use default {minutes} min")

        video_list.append((href, minutes, title))

    print(Fore.WHITE + "[Info] " + "="*10 + " Fetching complete " + "="*10)
    print(Fore.YELLOW + f"[Warning] Total {len(video_list)} videos to play")

    return video_list, driver


def loading_video(driver, v_time, name):
    """
    開啟影片頁面並播放
    """
    # 點擊影片播放器控制項
    time.sleep(2)
    driver.find_element(By.XPATH, '//*[@id="fsPlayer"]/div[10]/div[3]/div').click()
    driver.find_element(By.XPATH, '//*[@id="fsPlayer"]/div[10]/div[8]').click()

    print(f"{name} start")
    start_time = time.time()
    max_time = int(v_time) * 30 + 60  # 加 60 秒 buffer

    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time >= max_time:
            break
        # 持續點擊影片
        back = driver.find_element(By.XPATH, '//*[@id="fsPlayer"]/div[9]')
        action = ActionChains(driver)
        action.double_click(back).perform()
        time.sleep(2)

    print(Fore.GREEN + f"{name} end")
    driver.quit()

def wrapped_loading_video(account, password, url, v_time, name):
    """
    用 semaphore 限制同時執行的影片數量
    """
    with semaphore:
        loading_video(account, password, url, v_time, name)


def start_videos(account, password, video_href_list):
    """
    開始多個影片播放
    """
    threads = []
    for url, v_time, name in video_href_list:
        thread = threading.Thread(target=wrapped_loading_video, args=(account, password, url, v_time, name))
        thread.start()
        threads.append(thread)

    # 等待所有影片結束
    for thread in threads:
        thread.join()
