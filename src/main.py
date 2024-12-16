import os
import re
import time
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains 
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
import threading
load_dotenv()
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(),options=chrome_options)

account = os.getenv("ACCOUNT")
password = os.getenv("PASSWORD")
#需要先手動報名
course_url = os.getenv("COURSE_URL")

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
except NoSuchElementException:
    pass

time.sleep(1)
driver.get(course_url)
video_list  = []
video_block =  driver.find_elements(by=By.CLASS_NAME,value='center-part')

for i in video_block:
    temp = i.find_elements(by=By.XPATH,value='div')
    try:
        temp1 = i.find_element(by=By.XPATH,value='div/div[4]/span')
        continue
    except NoSuchElementException:
        pass
    temp2 = i.find_element(by=By.XPATH,value='span/div[1]')
    for j in temp:
        if j.text.find(">") != -1:
            numbers = re.findall(r'\d+', j.text)
            video_list.append((i,numbers[0],temp2.text))

video_href = []

for i,v_time,name in video_list:
    video_href.append((i.find_element(by=By.XPATH,value='./span/div[3]/div/div[1]/div[2]/a').get_property("href"),v_time,name))
print(video_href)

def loading_video(i,v_time,name):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(),options=chrome_options)
    driver.get(i)
    time.sleep(1)
    driver.find_element(by=By.XPATH,value='//*[@id="account"]/div/div[1]/input').send_keys(account)
    time.sleep(1)
    driver.find_element(by=By.XPATH,value='//*[@id="password"]/div/div[1]/div/input').send_keys(password)
    time.sleep(1)
    driver.find_element(by=By.XPATH,value='//*[@id="login_form"]/div[7]/div/button').click()
    time.sleep(3)
    try:
        button = driver.find_element(By.XPATH, '//*[@id="categoryForm"]/div[3]/div/a[2]')
        button.click()
    except NoSuchElementException:
        pass
    time.sleep(2)
    driver.find_element(by=By.XPATH,value='//*[@id="fsPlayer"]/div[10]/div[3]/div').click()
    time.sleep(2)
    driver.find_element(by=By.XPATH,value='//*[@id="fsPlayer"]/div[10]/div[8]').click()
    print(f"{name} start")
    start_time = time.time()
    max_time = int(v_time) * 60  + 60
    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time >= max_time:
            break
        back = driver.find_element(by=By.XPATH,value='//*[@id="fsPlayer"]/div[9]')
        action = ActionChains(driver)
        action.double_click(back)
        action.perform()
        time.sleep(2) 
    print(f"{name} end")

semaphore = threading.Semaphore(4)

def wrapped_loading_video(i, v_time, name):
    with semaphore:
        loading_video(i, v_time, name)

for i, v_time, name in video_href:
    thread = threading.Thread(target=wrapped_loading_video, args=(i, v_time, name))
    thread.start()
