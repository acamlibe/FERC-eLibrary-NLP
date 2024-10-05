import pandas as pd

import os
import requests
import random
import time


if not os.path.exists('downloads'):
    os.mkdir('downloads')

df = pd.read_csv('documents-list.csv')

filtered_df = df[df['File Id'] != '0']
filtered_df = filtered_df[['Project Numbers', 'File Id']]

filtered_df = filtered_df.dropna()



PROCESSED_FILE_NAME = 'processed_file_ids.txt'
FAILED_FILES_NAME = 'failed_file_ids.txt'

def load_file_lines(filename):
    try:
        with open(filename, 'r') as file:
            return set(line.strip() for line in file)
    except FileNotFoundError:
        return set()

def append_line(filename, line):
    with open(filename, 'a') as file:
        file.write(line + '\n')

processed_file_ids = load_file_lines(PROCESSED_FILE_NAME)
failed_file_ids = load_file_lines(FAILED_FILES_NAME)

def download_file(proj_number, file_id):
    url = 'https://elibrary.ferc.gov/eLibrarywebapi/api/File/DownloadP8File'

    headers = {
        'Content-Type': 'application/json'
    }

    body = {
        "FileType": "",
        "accession": "",
        "fileid": 0,
        "FileIDAll": "",
        "fileidLst": [
            file_id
        ],
        "Islegacy": False
    }

    response = requests.post(url=url, json=body, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # The folder where the file should be saved
        folder_path = os.path.join(os.getcwd(), 'downloads', proj_number)
        
        # Assuming the file name comes from headers or can be determined
        file_name = f"{file_id}.pdf"  # Modify this based on the file type you're expecting
        
        # Full path for the file
        file_path = os.path.join(folder_path, file_name)
        
        # Write the content to the file
        with open(file_path, 'wb') as file:
            file.write(response.content)
        
        print(f"File {file_name} downloaded successfully to {folder_path}")
    else:
        failed_file_ids.add(file_id)
        append_line(FAILED_FILES_NAME, file_id)
        print(f"Failed to download the file. Status code: {response.status_code} {response.text} {file_id}")



for index, row in filtered_df.iterrows():
    proj_numbers = row['Project Numbers']
    file_ids = row['File Id']
    
    if '|' in proj_numbers:
        proj_numbers = proj_numbers.split('|')
    else:
        proj_numbers = [proj_numbers]
    
    if '|' in file_ids:
        file_ids = file_ids.split('|')
    else:
        file_ids = [file_ids]

    for proj_number in proj_numbers:
        print('Processing Project Number: ', proj_number)

        if proj_number == '0':
            print('Skipping due to 0 project number')
            continue

        path = os.path.join('downloads', proj_number)

        if not os.path.exists(path):
            os.mkdir(path)

        for file_id in file_ids:
            print('Processing File Id: ', file_id)

            if file_id == '0':
                print('Skipping due to 0 file id')
                continue

            if file_id in processed_file_ids:
                print('Skipping file id already processed')
                continue

            download_file(proj_number, file_id)
            
            processed_file_ids.add(file_id)
            append_line(PROCESSED_FILE_NAME, file_id)

            seconds = random.randint(3, 10)

            print(f'Sleeping {seconds} seconds')
            time.sleep(seconds)