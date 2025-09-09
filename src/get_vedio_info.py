from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
import math
import re
from colorama import Fore, init
init(autoreset=True)

def need_to_skip_or_not(block):
    try:
        pass_condition_elem = block.find_element(By.CSS_SELECTOR, '.col-char7')
        pass_condition_text = pass_condition_elem.text.strip()
    except NoSuchElementException:
        pass_condition_text = ""
    if  re.search(r'須填寫', pass_condition_text) or \
         re.search(r'\s*\d+\s*分及格', pass_condition_text):
        print(Fore.YELLOW + f"[Info] Skip {block.text[:30]}... due to pass condition: {pass_condition_text}")
        return True
    return False

def get_vedio_title(block):
    try:
        title_elem = block.find_element(By.CSS_SELECTOR, 'a[href^="/media/"] span.text')
        title = title_elem.text.strip()
    except NoSuchElementException:
        title = "Unknown Title"
    print(Fore.BLUE + f"Processing video: {title}")
    return title

def get_vedio_link(block, title):
    try:
        link_elem = block.find_element(By.CSS_SELECTOR, 'a[href^="/media/"]')
        href = link_elem.get_attribute("href")
    except NoSuchElementException:
        print(Fore.RED + f"[Danger] No href found for {title}, skip")
        return None
    print(Fore.GREEN + f"[Success] Found video link: {href}")
    return href

def get_vedio_time(block, title):
    minutes = 5
    time_text = ""

    try:
        toggle_btn = block.find_element(By.CSS_SELECTOR, 'a.mobile_ext-btn')
        if toggle_btn.get_attribute('aria-expanded') != 'true':
            ActionChains(block).move_to_element(toggle_btn).click().perform()
            WebDriverWait(block, 2).until(
                lambda d: toggle_btn.get_attribute('aria-expanded') == 'true'
            )
    except NoSuchElementException:
        pass

    if block.find_elements(By.CSS_SELECTOR, "span.item-pass"):
        print(Fore.GREEN + f"[Pass] {title} 已通過 ✅")
        return 0

    try:
        dl_elem = block.find_element(By.CSS_SELECTOR, 'div.fs-description dl')
        dt_elements = dl_elem.find_elements(By.TAG_NAME, 'dt')
        dd_elements = dl_elem.find_elements(By.TAG_NAME, 'dd')

        for dt, dd in zip(dt_elements, dd_elements):
            dt_text = dt.get_attribute('innerText').strip()
            if '通過條件' in dt_text:
                time_text = dd.get_attribute('innerText').strip()
                break
    except NoSuchElementException:
        pass

    print(Fore.WHITE + f"[Info] Found time text: {time_text}")

    if "分鐘" in time_text:
        minutes = int(re.search(r'\d+', time_text).group())
    elif "次" in time_text:
        times = int(re.search(r'\d+', time_text).group())
        minutes = 1 if times >= 1 else times 

    watched_minutes = 0
    try:
        watched_elem = block.find_element(By.CSS_SELECTOR, "a[data-url*='readTime'] span.text")
        watched_text = watched_elem.get_attribute("innerText").strip()
        if ":" in watched_text:
            m, s = map(int, watched_text.split(":"))
            watched_minutes = m + math.floor(s / 60)
        elif watched_text.isdigit():
            watched_minutes = int(watched_text)
    except NoSuchElementException:
        pass

    if watched_minutes >= minutes:
        print(Fore.GREEN + f"[Pass] {title} 已看完 ✅ ({watched_minutes}/{minutes} 分鐘)")
        return 0

    remaining = max(minutes - watched_minutes, 0)
    print(Fore.YELLOW + f"[Info] {title} 觀看進度: {watched_minutes}/{minutes} 分鐘，剩餘 {remaining} 分鐘")
    return remaining
