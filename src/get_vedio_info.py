import re
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
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
    try:
        time_elem = block.find_element(By.CSS_SELECTOR, '.hidden-xs.pull-right .col-char7')
        time_text = time_elem.text.strip()
        print(Fore.WHITE + f"[Info] Found time text: {time_text}")
        minutes = 5
        if "分鐘" in time_text:
            print(Fore.GREEN + f"[Success] Found time text: {time_text}")
            minutes = int(re.search(r'\d+', time_text).group())
        elif "次" in time_text:
            print(Fore.GREEN + f"[Success] Found time text: {time_text}")
            times = int(re.search(r'\d+', time_text).group())
            minutes = times * 0.1
        else:
            if "分鐘" in title:
                minutes = int(re.search(r'\d+', title).group())
                print(Fore.GREEN + f"[Success] Found video duration: {minutes} min")
            elif "次" in title:
                times = int(re.search(r'\d+', title).group())
                minutes = times * 0.1
        print(Fore.GREEN + f"[Success] Found video duration: {minutes} min")
    except NoSuchElementException:
        minutes = 5
        print(Fore.YELLOW + f"[Warning] No time info for {title}, use default {minutes} min")
    return minutes