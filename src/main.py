import os
import re
import time
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains 
from dotenv import load_dotenv
load_dotenv()
driver = webdriver.Chrome(service=Service())

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
    button = driver.find_element(By.XPATH, '//*[@id="categoryForm"]/div[3]/div/a[1]')
    print("element exists")
    button.click()
except NoSuchElementException:
    print("element not found")
time.sleep(1)
driver.get(course_url)
video_list  = []
video_block =  driver.find_elements(by=By.CLASS_NAME,value='center-part')[1:]

for i in video_block:
    temp = i.find_elements(by=By.XPATH,value='div')
    for j in temp:
        if j.text.find(">") != -1:
            numbers = re.findall(r'\d+', j.text)
            video_list.append((i,numbers[0]))

video_href = []
for i,v_time in video_list:
    video_href.append((i.find_element(by=By.XPATH,value='./span/div[3]/div/div[1]/div[2]/a').get_property("href"),v_time))

for i,v_time in video_href:
    driver.get(i)
    time.sleep(2)
    driver.find_element(by=By.XPATH,value='//*[@id="fsPlayer"]/div[10]/div[3]/div').click()
    time.sleep(2)
    driver.find_element(by=By.XPATH,value='//*[@id="fsPlayer"]/div[10]/div[8]').click()
    start_time = time.time()
    max_time = int(v_time) * 60  + 10
    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time >= max_time:
            break
        back = driver.find_element(by=By.XPATH,value='//*[@id="fsPlayer"]/div[9]')
        action = ActionChains(driver)
        action.double_click(back)
        action.perform()
        print(f"{(elapsed_time/max_time)*100:.2f}%")
        time.sleep(2) 