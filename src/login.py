import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from colorama import Fore, init
init(autoreset=True)

def login(driver, account, password):
    driver.get("https://tms.utaipei.edu.tw/index/login")

    driver.find_element(By.NAME, "account").send_keys(account)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, 'button[data-role="form-submit"]').click()
    time.sleep(3)

    try:
        driver.find_element(By.CSS_SELECTOR, 'a.keepLoginBtn').click()
        print(Fore.YELLOW + "[Warning] " + "Pop up handled")
    except NoSuchElementException:
        print(Fore.RED + "[Danger] " + "No pop up")
        pass
    time.sleep(3)
    if "login" in driver.current_url:
        print(Fore.RED + "[Danger] " + "Login failed, please check your ACCOUNT and PASSWORD in .env file")
        exit(1)
    else:
        print(Fore.WHITE + "[Info] current url: " + driver.current_url)
    print(Fore.GREEN + "Login success")