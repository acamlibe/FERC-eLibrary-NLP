from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

import time
import cgi
import os
from urllib.request import urlopen, urlretrieve

def load_file_lines(filename):
    try:
        with open(filename, 'r') as file:
            return set(line.strip() for line in file)
    except FileNotFoundError:
        return set()

def append_line(filename, line):
    with open(filename, 'a') as file:
        file.write(line + '\n')


clicked_documents = load_file_lines('clicked_documents.txt')
processed_urls = load_file_lines('processed_urls.txt')

driver = webdriver.Chrome()

driver.maximize_window()

driver.get('https://hydropowerelibrary.pnnl.gov/Documents')

time.sleep(5)

driver.find_element(By.XPATH, "/html/body/div/div/div/div/main/section[2]/div/div/section/button").click()

def get_documents_list():
    documents_container = driver.find_element(By.XPATH, "/html/body/div/div/div/div/main/section[2]/div/div/div/div[2]")
    return driver.execute_script('return arguments[0].children;', documents_container)

def get_files_list():
    files_list = driver.find_element(By.XPATH, "/html/body/div/div/div/div/main/section/div/ul")
    return driver.execute_script('return arguments[0].children;', files_list)

def download_file(url, project_name):
    if not os.path.exists(f'files/{project_name}'):
        os.makedirs(f'files/{project_name}')
    remote = urlopen(url)
    content = remote.info()['Content-Disposition']
    _, params = cgi.parse_header(content)
    file_name = params['filename'].replace(' ', '_')
    path = f'files/{project_name}/{file_name}'
    urlretrieve(url, path)


def process_document(document):
    inner_div = document.find_element(By.TAG_NAME, 'div')

    title = inner_div.text.split('\n')[0]

    if title in clicked_documents:
        return

    clicked_documents.add(title)
    append_line('clicked_documents.txt', title)

    ActionChains(driver).key_down(Keys.CONTROL).click(inner_div).key_up(Keys.CONTROL).perform()
    time.sleep(1)
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(3)

    if 'Document Contents Not Publicly Available' not in driver.page_source:
        plant_id = driver.find_element(By.XPATH, "/html/body/div/div/div/div/main/article/section[1]/div/ul/li/a/div/h4/span[1]")
        print(plant_id.text)

        files_elements = get_files_list()
        for element in files_elements:
            span = element.find_element(By.TAG_NAME, 'span')
            anchor = span.find_element(By.TAG_NAME, 'a')
            href = anchor.get_attribute('href')
            if href in processed_urls:
                continue
            download_file(href, plant_id.text)
            processed_urls.add(href)
            append_line('processed_urls.txt', href)

    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    
scrolling_container = driver.find_element(By.XPATH, "/html/body/div/div/div/div/main/section[2]/div/div")

last_height = driver.execute_script("return arguments[0].scrollHeight", scrolling_container)
scroll_increment = 400  # Amount to scroll in each iteration

while True:
    documents = get_documents_list()

    for doc in documents:
        process_document(doc)

    current_scroll_top = driver.execute_script("return arguments[0].scrollTop", scrolling_container)
    
    # Scroll down by a smaller increment
    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollTop + arguments[1]", scrolling_container, scroll_increment)
    
    time.sleep(2)

    new_height = driver.execute_script("return arguments[0].scrollHeight", scrolling_container)
    new_scroll_top = driver.execute_script("return arguments[0].scrollTop", scrolling_container)

    # If there's no change in height or scrollTop, stop
    if new_height == last_height and new_scroll_top == current_scroll_top:
        break

    last_height = new_height



driver.quit()