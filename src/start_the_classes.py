import time
import threading
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv
from colorama import Fore, init
init(autoreset=True)

from utils import create_driver, check_current_dom, open_all_buttons, check_if_its_login, copy_cookies
from get_vedio_info import need_to_skip_or_not, get_vedio_title, get_vedio_link, get_vedio_time
from login import login

semaphore = threading.Semaphore(3) # control the number of concurrent video playbacks

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

    if not check_if_its_login(driver):
        print(Fore.RED + "[Danger] " + "Not on login page")
        exit(1)

    video_list = []

    open_all_buttons(driver) # test

    # 等待影片區塊出現
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

    print(Fore.WHITE + "[Info] " + "="*10 + " Fetching complete " + "="*10)
    print(Fore.YELLOW + f"[Warning] Total {len(video_list)} videos to play")
    print(Fore.YELLOW + f"[Warning] Total video time: {total_video_time} minutes")

    return video_list, driver


def loading_video(driver, v_time, name):
    """
    開啟影片頁面並播放
    """
    # 點擊影片播放器控制項
    time.sleep(2)

    print(f"{name} start - {v_time} minutes")
    start_time = time.time()
    max_time = int(v_time) * 60 + 60  # 加 60 秒 buffer

    try:
        play_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'fs-playBtn'))
        )
        play_btn.click()
        driver.find_element(By.XPATH, '//*[@id="fsPlayer"]/div[10]/div[8]').click()
    except Exception as e:
        print(Fore.RED + f"[Error] Cannot find video player buttons: {e}")
        return
    
    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time >= max_time:
            break
        # 持續點擊影片
        try:
            back = driver.find_element(By.XPATH, '//*[@id="fsPlayer"]/div[9]')
            ActionChains(driver).double_click(back).perform()
            time.sleep(2)
        except Exception as e:
            print(f"[Warning] Error during video playback: {e}")


    print(Fore.GREEN + f"{name} end")

def start_videos(driver, debug_mode, video_href_list):
    """
    開始多個影片播放
    """
    for url, v_time, name in video_href_list:
        driver.get(url)
        loading_video(driver, v_time, name)
    driver.quit()
