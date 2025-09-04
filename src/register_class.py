from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from colorama import Fore, init
init(autoreset=True)


def registering_class(driver, class_url):
    """
    Register a new class
    """
    driver.get(class_url)
    try:
        element = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//a[.//span[text()='報名']]"))
        )
        driver.execute_script("arguments[0].click();", element)
        print(Fore.GREEN + "Registration successful")
    except NoSuchElementException:
        print(Fore.YELLOW + "[Warning] " + "Already registered")
