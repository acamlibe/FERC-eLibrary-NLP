from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

import time
import cgi
import os
from urllib.request import urlopen, urlretrieve

processed_projects_path = 'processed_projects.txt'
processed_documents_path = 'processed_documents.txt'
processed_urls_path = 'processed_urls.txt'

def load_file_lines(filename):
    try:
        with open(filename, 'r') as file:
            return set(line.strip() for line in file)
    except FileNotFoundError:
        return set()

def append_line(filename, line):
    with open(filename, 'a') as file:
        file.write(line + '\n')

def download_file(url, project_id):
    folder_path = f'files/{project_id}'

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    remote = urlopen(url)
    content = remote.info()['Content-Disposition']
    _, params = cgi.parse_header(content)
    file_name = params['filename'].replace(' ', '_')
    path = f'{folder_path}/{file_name}'
    urlretrieve(url, path)


processed_projects = load_file_lines(processed_projects_path)
processed_documents = load_file_lines(processed_documents_path)
processed_urls = load_file_lines(processed_urls_path)


driver = webdriver.Chrome()

driver.maximize_window()

driver.get('https://hydropowerelibrary.pnnl.gov/Projects')

time.sleep(5)

driver.find_element(By.XPATH, "/html/body/div/div/div/div/main/section[2]/div/div/section/button").click()

def get_documents(document_div, project_id):
    inner_div = document_div.find_element(By.TAG_NAME, 'div')

    title = inner_div.text.split('\n')[0]

    if title in processed_documents:
        return
    
    ActionChains(driver).key_down(Keys.CONTROL).click(inner_div).key_up(Keys.CONTROL).perform()
    time.sleep(1)
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(3)

    if 'Document Contents Not Publicly Available' not in driver.page_source:
        files_list = driver.find_element(By.XPATH, "/html/body/div/div/div/div/main/section/div/ul")
        files = driver.execute_script('return arguments[0].children;', files_list)
        for element in files:
            if 'No Filename' in element.text:
                continue

            anchor = element.find_element(By.XPATH, ".//a[contains(@href, 'attachment')]")
            href = anchor.get_attribute('href')
            
            if href in processed_urls:
                continue
            download_file(href, project_id)
            processed_urls.add(href)
            append_line(processed_urls_path, href)

    processed_documents.add(title)
    append_line(processed_documents_path, title)

    driver.close()
    driver.switch_to.window(driver.window_handles[1])

def open_project(project_div):
    inner_div = project_div.find_element(By.TAG_NAME, 'div')

    proj_anchor = inner_div.find_element(By.TAG_NAME, 'a')
    proj_href = proj_anchor.get_attribute('href')

    project_id = proj_href.split('/')[-1]

    if project_id in processed_projects:
        return
    
    ActionChains(driver).key_down(Keys.CONTROL).click(inner_div).key_up(Keys.CONTROL).perform()
    time.sleep(1)
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(3)

    project_id_element = driver.find_element(By.XPATH, "/html/body/div/div/div/div/main/article/header/h2/span[1]")
    project_id = project_id_element.text
    # site_name = driver.find_element(By.XPATH, "/html/body/div/div/div/div/main/article/header/h2/span[3]")

    scrolling_documents = driver.find_element(By.XPATH, "/html/body/div/div/div/div/main/section/div/div")
    last_height2 = driver.execute_script("return arguments[0].scrollHeight", scrolling_documents)
    scroll_increment2 = 400  # Amount to scroll in each iteration
    while True:
        documents_container = driver.find_element(By.XPATH, "/html/body/div/div/div/div/main/section/div/div/div/div[2]")
        documents = driver.execute_script('return arguments[0].children;', documents_container)
        for doc in documents:
            get_documents(doc, project_id)

        current_scroll_top = driver.execute_script("return arguments[0].scrollTop", scrolling_documents)
        
        # Scroll down by a smaller increment
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollTop + arguments[1]", scrolling_documents, scroll_increment2)
        
        time.sleep(2)

        new_height = driver.execute_script("return arguments[0].scrollHeight", scrolling_documents)
        new_scroll_top = driver.execute_script("return arguments[0].scrollTop", scrolling_documents)

        # If there's no change in height or scrollTop, stop
        if new_height == last_height2 and new_scroll_top == current_scroll_top:
            break

        last_height2 = new_height

    processed_projects.add(project_id)
    append_line(processed_projects_path, project_id)

    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    
scrolling_projects = driver.find_element(By.XPATH, "/html/body/div/div/div/div/main/section[2]/div/div")

last_height = driver.execute_script("return arguments[0].scrollHeight", scrolling_projects)
scroll_increment = 400  # Amount to scroll in each iteration

while True:
    projects_container = driver.find_element(By.XPATH, "/html/body/div/div/div/div/main/section[2]/div/div/div/div[2]")
    projects = driver.execute_script('return arguments[0].children;', projects_container)

    for project in projects:
        open_project(project)

    current_scroll_top = driver.execute_script("return arguments[0].scrollTop", scrolling_projects)
    
    # Scroll down by a smaller increment
    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollTop + arguments[1]", scrolling_projects, scroll_increment)
    
    time.sleep(2)

    new_height = driver.execute_script("return arguments[0].scrollHeight", scrolling_projects)
    new_scroll_top = driver.execute_script("return arguments[0].scrollTop", scrolling_projects)

    # If there's no change in height or scrollTop, stop
    if new_height == last_height and new_scroll_top == current_scroll_top:
        break

    last_height = new_height



driver.quit()