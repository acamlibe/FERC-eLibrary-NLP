from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import os
import nltk
import psycopg2
import glob

nltk.download('punkt')
nltk.download('punkt_tab')

FILES_FOLDER = f'../TextExtractor/files'

MODEL = 'philschmid/bart-large-cnn-samsum'

tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL)

conn = psycopg2.connect(database='fercsummary', host='localhost', port='5432', user='alic', password='FercSummary!')


def chunk_text(sentences):
    length = 0
    chunk = ''
    all_chunks = []
    counter = -1

    for sentence in sentences:
        counter += 1
        combined_length = len(tokenizer.tokenize(sentence)) + length

        if combined_length <= tokenizer.max_len_single_sentence:
            chunk += sentence + ' '
            length = combined_length

            if counter == len(sentences) - 1:
                all_chunks.append(chunk.strip())
        else:
            all_chunks.append(chunk.strip())
            length = 0
            chunk = ''

            chunk += sentence + ' '
            length = len(tokenizer.tokenize(sentence))

    return all_chunks


def summarize(text):
    sentences = nltk.tokenize.sent_tokenize(text)
    all_chunks = chunk_text(sentences)

    chunk_summary_inputs = [tokenizer(chunk, return_tensors="pt") for chunk in all_chunks]

    chunk_summaries = []

    for input in chunk_summary_inputs:
        output = model.generate(**input)
        summary = tokenizer.decode(*output, skip_special_tokens=True)
        chunk_summaries.append(summary)

    return ' '.join(chunk_summaries)

def already_summarized(project_id, extracted_file_name):
    cursor = conn.cursor()
    cursor.execute('SELECT project_id FROM public.summary WHERE project_id = %s AND extracted_file_name = %s', (project_id, extracted_file_name))
    exists = cursor.fetchone() is not None
    cursor.close()
    return exists


def save_project(project_id, summarizations):
    cursor = conn.cursor()

    for summary in summarizations:
        proj_folder = os.path.join('../APIScraper/downloads', project_id)
        file_path = ''
        for infile in glob.glob(os.path.join(proj_folder, f'{summary['file_name'].replace('.txt', '')}.*')):
            file_path = infile
            break

        original_file_name = os.path.basename(file_path)
        extracted_file_name = summary['file_name']

        file_text = summary['file_text']
        summary_text = summary['summary_text']

        with open(file_path, 'rb') as f:
            ba = f.read()
            cursor.execute("INSERT INTO public.summary (summary_text, project_id, original_file_name, file_text, file_binary, extracted_file_name) VALUES (%s, %s, %s, %s, %s, %s)",
                   (summary_text, project_id, original_file_name, file_text, ba, extracted_file_name))
            
    conn.commit()
    cursor.close()


summarizations = []

project_ids = [name for name in os.listdir(FILES_FOLDER) if os.path.isdir(os.path.join(FILES_FOLDER, name))]

for project_id in project_ids:
    print(f'Processing {project_id}')

    for file_name in os.listdir(os.path.join(FILES_FOLDER, project_id)):

        if already_summarized(project_id, file_name):
            print(f'Skipping/Already Summarized : {file_name}')
            continue

        print(f'Summarizing {file_name}')
        path = os.path.join(FILES_FOLDER, project_id, file_name)

        with open(path, 'r') as file:
            text = file.read().strip()

        try:
            summary = summarize(text)
        except:
            continue

        summarizations.append({'summary_text': summary, 'file_name': file_name, 'file_text': text })

    if len(summarizations) > 0:
        save_project(project_id, summarizations)

    summarizations = []
    

