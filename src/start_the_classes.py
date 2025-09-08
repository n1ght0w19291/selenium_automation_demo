import time
import threading
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from colorama import Fore, init
import math
init(autoreset=True)

from utils import create_driver, open_all_buttons, is_logged_in
from get_vedio_info import need_to_skip_or_not, get_vedio_title, get_vedio_link, get_vedio_time
from login import login

semaphore = threading.Semaphore(10)

def start_class(driver, course_url, debug_mode):
    print(Fore.WHITE + "[Info] " + "="*10 + " Start fetching video links " + "="*10)
    print(Fore.WHITE + "[Info] " + "Navigating to course page " + course_url)
    driver.get(course_url)

    print(Fore.WHITE + "[Info] " + "current URL: " + driver.current_url)

    total_video_time = 0

    if driver.current_url != course_url:
        print(Fore.RED + "[Danger] " + "Failed to navigate to course page")
        try:
            course_link_elem = driver.find_element(By.CSS_SELECTOR, "ol.breadcrumb li:nth-child(2) a")
            href = course_link_elem.get_attribute("href")
            title = course_link_elem.text.strip()
            print(Fore.WHITE + f"[Info] Found course link: {title} -> {href}")
            driver.get(href)
        except Exception as e:
            print(Fore.RED + "[Error] Failed to get course link:", e)
            exit(1)
    else:
        print(Fore.YELLOW + "[Warning] " + "Successfully navigated to course page")

    if not is_logged_in(driver):
        print(Fore.RED + "[Danger] " + "Not on login page")
        exit(1)

    video_list = []

    open_all_buttons(driver)

    time.sleep(3)
    video_blocks = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.center-part > span.xtree-node-label"))
    )
    print(Fore.YELLOW + f"[Warning] Found {len(video_blocks)} video blocks")

    for block in video_blocks:
        skip = need_to_skip_or_not(block)
        if skip:
            continue

        title = get_vedio_title(block)
        link = get_vedio_link(block, title)
        if not link:
            continue
        duration = get_vedio_time(block, title)
        if duration == 0:
            continue
        total_video_time += duration

        video_list.append((link, duration, title))

    video_list.sort(key=lambda x: x[1], reverse=True)
    print(Fore.WHITE + "[Info] " + "="*10 + " Fetching complete " + "="*10)
    print(Fore.YELLOW + f"[Warning] Total {len(video_list)} videos to play")
    print(Fore.YELLOW + f"[Warning] Total video time: {total_video_time} minutes")

    return video_list, driver


def loading_video(driver, v_time, name):
    """
    開啟影片頁面並播放
    """
    time.sleep(2)

    print(f"{name} start - {v_time} minutes")
    start_time = time.time()
    max_time = math.ceil(v_time) * 60 + 60

    try:
        driver.find_element(by=By.XPATH,value='//*[@id="fsPlayer"]/div[10]/div[3]/div').click()
        time.sleep(2)
        driver.find_element(by=By.XPATH,value='//*[@id="fsPlayer"]/div[10]/div[8]').click()
    except Exception as e:
        print(Fore.RED + f"[Error] Cannot find video player buttons: {e}")
        return
    
    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time >= max_time:
            break
        try:
            back = driver.find_element(By.XPATH, '//*[@id="fsPlayer"]/div[9]')
            ActionChains(driver).double_click(back).perform()

            time.sleep(2)
        except Exception as e:
            print(f"[Warning] Error during video playback: {e}")


    print(Fore.GREEN + f"{name} end")

def thread_worker(account, password, debug_mode, url, v_time, name):
    with semaphore:
        driver = create_driver(not debug_mode)
        driver.get("https://tms.utaipei.edu.tw/")
        login(driver, account, password)
        driver.get(url)

        loading_video(driver, v_time, name)
        driver.quit()

def start_videos(account, password, debug_mode, video_href_list):
    """
    開始多個影片播放
    """
    threads = []
    for url, v_time, name in video_href_list:
        t = threading.Thread(target=thread_worker, args=(account, password, debug_mode, url, v_time, name))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()