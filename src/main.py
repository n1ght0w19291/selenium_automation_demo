import os
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
from colorama import Fore, init
init(autoreset=True)

# own script import
from login import login
from register_class import registering_class
from start_the_classes import start_class, start_videos
from utils import copy_cookies, create_driver

load_dotenv()
account = os.getenv("ACCOUNT")
password = os.getenv("PASSWORD")
class_code = os.getenv("COURSE_CODE")
debug_mode = os.getenv("DEBUG")

if not account or not password or not class_code:
    print(Fore.RED + "[Danger] " + "Please set ACCOUNT, PASSWORD, and COURSE_CODE in .env file")
    exit(1)

driver = create_driver(not debug_mode)

# 登入
login(driver, account, password)

# 報名課程
registering_class(driver, f"https://tms.utaipei.edu.tw/course/syllabus?courseId={class_code}")

print(Fore.WHITE + "[Info] " + "=" * 10 + " Start the classes " + "=" * 10)

video_href_list = start_class(driver, f"https://tms.utaipei.edu.tw/course/{class_code}", debug_mode)

# 播放影片，每個 thread 自己建立 driver
start_videos(account, password, video_href_list)

print(Fore.WHITE + "[Info] " + "=" * 10 + " Done！ " + "=" * 10)