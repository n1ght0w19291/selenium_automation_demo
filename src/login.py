import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from colorama import Fore, init
init(autoreset=True)

def login(driver, account, password):
    driver.get("https://tms.utaipei.edu.tw/index/login")

    driver.find_element(by=By.XPATH,value='//*[@id="account"]/div/div[1]/input').send_keys(account)
    time.sleep(1)
    driver.find_element(by=By.XPATH,value='//*[@id="password"]/div/div[1]/div/input').send_keys(password)
    time.sleep(1)
    driver.find_element(by=By.XPATH,value='//*[@id="login_form"]/div[7]/div/button').click()
    time.sleep(3)

    try:
        button = driver.find_element(By.XPATH, '//*[@id="categoryForm"]/div[3]/div/a[2]')
        button.click()
        print(Fore.YELLOW + "[Warning] " + "Pop up handled")
    except NoSuchElementException:
        print(Fore.RED + "[Danger] " + "No pop up")
        pass

    print(Fore.GREEN + "Login success")