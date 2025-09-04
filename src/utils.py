from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from colorama import Fore, Style, init
init(autoreset=True)


def create_driver(headless=True):
    options = Options()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--log-level=3")
    service = Service(log_path="NUL")
    return webdriver.Chrome(service=service, options=options)
