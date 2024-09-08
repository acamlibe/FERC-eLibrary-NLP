import os
import pdfplumber
from docx import Document
import pytesseract
from PIL import Image
import re
import subprocess

FILES_DIR = '../Scraper/files'
EXTRACTED_DIR = 'files'

if not os.path.exists(EXTRACTED_DIR):
    os.makedirs(EXTRACTED_DIR)

def read_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text()
        return text

def read_docx(file_path):
    doc = Document(file_path)
    return '\n'.join([para.text for para in doc.paragraphs])


def read_tif(file_path):
    image = Image.open(file_path)
    return pytesseract.image_to_string(image)

def read_txt(file_path):
    with open(file_path, 'r', encoding='iso-8859-1') as file:
        return file.read()
    
def read_wpd(file_path):
    temp_dir = 'temp'
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)

    file_name = os.path.basename(file_path)
    output_file_base = re.sub(r'\.wpd$', '.txt', file_name, flags=re.IGNORECASE)  # Case-insensitive replace
    temp_path = os.path.join(temp_dir, output_file_base)

    subprocess.run([
        'soffice',  # Path to LibreOffice
        '--headless',  # Run without a GUI
        '--convert-to', 'txt',  # Convert to text format
        file_path,  # Input file
        '--outdir', temp_dir  # Output directory
    ], check=True)

    with open(temp_path, 'r', encoding='utf-8', errors='ignore') as file:
        return file.read()
    

def read_doc(file_path):
    temp_dir = 'temp'
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)

    file_name = os.path.basename(file_path)
    output_file_base = re.sub(r'\.doc$', '.txt', file_name, flags=re.IGNORECASE)  # Case-insensitive replace
    temp_path = os.path.join(temp_dir, output_file_base)

    subprocess.run([
        'soffice',  # Path to LibreOffice
        '--headless',  # Run without a GUI
        '--convert-to', 'txt',  # Convert to text format
        file_path,  # Input file
        '--outdir', temp_dir  # Output directory
    ], check=True)

    with open(temp_path, 'r', encoding='utf-8', errors='ignore') as file:
        return file.read()


for project_folder in os.listdir(FILES_DIR):
    project_dir = os.path.join(FILES_DIR, project_folder)

    for document in os.listdir(project_dir):
        file_path = os.path.join(project_dir, document)

        file_name, extension = os.path.splitext(document)

        extracted_file_dir = os.path.join(EXTRACTED_DIR, project_folder)
        extracted_file_path = os.path.join(extracted_file_dir, file_name + '.txt')

        if os.path.exists(extracted_file_path):
            continue

        if not os.path.exists(extracted_file_dir):
            os.mkdir(extracted_file_dir)

        extension = extension.lower()

        text = ''

        match extension:
            case '.pdf': text = read_pdf(file_path)
            case '.docx': text = read_docx(file_path)
            case '.doc': text = read_doc(file_path)
            case '.tif' | '.tiff': text = read_tif(file_path)
            case '.txt': text = read_txt(file_path)
            case '.wpd': text = read_wpd(file_path)
            case _: continue

        with open(extracted_file_path, 'w+') as file:
            file.write(text)