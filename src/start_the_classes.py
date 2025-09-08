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

semaphore = threading.Semaphore(4) # control the number of concurrent video playbacks

def start_class(driver2, course_url, debug_mode):
    print(Fore.WHITE + "[Info] " + "="*10 + " Start fetching video links " + "="*10)
    driver = create_driver(not debug_mode)
    driver.get("https://tms.utaipei.edu.tw/")
    copy_cookies(driver2, driver, debug_mode)
    driver2.quit()
    print(Fore.WHITE + "[Info] " + "Navigating to course page " + course_url)
    driver.get(course_url)

    print(Fore.WHITE + "[Info] " + "current URL: " + driver.current_url)

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

    print(Fore.BLUE + "Current blocks: " + "\n\n".join([b.get_attribute('outerHTML') for b in video_blocks[:4]]))

    for block in video_blocks:
        skip = need_to_skip_or_not(block)
        if skip:
            continue

        title = get_vedio_title(block)
        link = get_vedio_link(block, title)
        if not link:
            continue
        duration = get_vedio_time(block, title)

        video_list.append((link, duration, title))

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
    max_time = int(v_time) * 60 + 60  # 加 60 秒 buffer

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
    driver.quit()

def wrapped_loading_video(cookies, debug_mode, url, v_time, name):
    """
    用 semaphore 限制同時執行的影片數量
    """
    if "https://tms.utaipei.edu.tw/course/" not in url:
        print(Fore.RED + "[Danger] " + f"Invalid video URL: {url}")
        return
    with semaphore:
        driver = create_driver(not debug_mode)
        driver.get("https://tms.utaipei.edu.tw/")
        for cookie in cookies:
            if "sameSite" in cookie:
                cookie.pop("sameSite")
            driver.add_cookie(cookie)
        print(Fore.WHITE + "[Info] " + f"Starting video: {name} ({url}) for {v_time} minutes")
        driver.get(url)
        loading_video(driver, v_time, name)

def start_videos(account, password, debug_mode, video_href_list):
    """
    開始多個影片播放
    """
    threads = []
    
    driver_main = create_driver(not debug_mode)
    login(driver_main, account, password)
    cookies = driver_main.get_cookies()
    driver_main.quit()
    for url, v_time, name in video_href_list:
        thread = threading.Thread(target=wrapped_loading_video, args=(cookies, debug_mode, url, v_time, name))
        thread.start()
        threads.append(thread)

    # 等待所有影片結束
    for thread in threads:
        thread.join()
