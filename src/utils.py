import time
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from colorama import Fore, Style, init
init(autoreset=True)


def create_driver(headless=True):
    options = Options()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--log-level=3")
    service = Service(log_path="NUL")
    return webdriver.Chrome(service=service, options=options)

def check_current_dom(elem):
    parent = elem.find_element(By.XPATH, '..')  # 取得父節點
    print(parent.get_attribute('outerHTML'))

    siblings = elem.find_elements(By.XPATH, 'following-sibling::*')
    for s in siblings:
        print(s.get_attribute('outerHTML'))

def open_all_buttons(driver):
    expand_buttons = driver.find_elements(By.CSS_SELECTOR, "a.mobile_ext-btn")
    print(Fore.YELLOW + f"[Warning] Found {len(expand_buttons)} expand buttons")
    for btn in expand_buttons:
        driver.execute_script("arguments[0].click();", btn)
        time.sleep(0.3)  # 等待 DOM 更新

def is_logged_in(driver):
    """
    Check if the current page is the login page
    """
    try:
        driver.find_element(By.XPATH, '//a[span[text()="登入"]]')
        print("尚未登入")
        return False
    except NoSuchElementException:
        print("已經登入")
        return True

def copy_cookies(driver1, driver2, debug_mode):
    """
    Copy cookies from one driver to another
    """
    cookies = driver1.get_cookies()
    for cookie in cookies:
        if debug_mode:
            print("[Debug] Copying cookie:", cookie)  # 檢查 domain
        if "sameSite" in cookie:
            cookie.pop("sameSite")  # 避免錯誤
        driver2.add_cookie(cookie)
    driver2.refresh()