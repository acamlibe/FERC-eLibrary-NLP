from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import os
import nltk
import psycopg2
import glob
from transformers import pipeline
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter, TokenTextSplitter


nltk.download('punkt')
nltk.download('punkt_tab')

FILES_FOLDER = f'../TextExtractor/files'

MODEL = 'philschmid/bart-large-cnn-samsum'

tokenizer = AutoTokenizer.from_pretrained("suriya7/bart-finetuned-text-summarization")
model = AutoModelForSeq2SeqLM.from_pretrained("suriya7/bart-finetuned-text-summarization")

conn = psycopg2.connect(database='fercsummary', host='localhost', port='5432', user='alic', password='FercSummary!')

text_splitter = TokenTextSplitter(
    # Set a really small chunk size, just to show.
    chunk_size=1000,
    chunk_overlap=0
)

def chunk_text(sentences, max_tokens=980):
    length = 0
    chunk = ''
    all_chunks = []
    
    for sentence in sentences:
        sentence_length = len(tokenizer.tokenize(sentence))

        if length + sentence_length <= max_tokens:
            chunk += sentence + ' '
            length += sentence_length
        else:
            # Append the completed chunk to all_chunks
            all_chunks.append(chunk.strip())
            # Start a new chunk with the current sentence
            chunk = sentence + ' '
            length = sentence_length

    # Append any remaining chunk after the loop
    if chunk.strip():
        all_chunks.append(chunk.strip())
        
    return all_chunks



def summarize(text):
    sentences = nltk.tokenize.sent_tokenize(text)
    all_chunks = text_splitter.split_text(text)

    # Tokenize the prompt inputs
    chunk_summary_inputs = [tokenizer(chunk, return_tensors="pt", truncation=True) for chunk in all_chunks]

    chunk_summaries = []

    for input in chunk_summary_inputs:
        output = model.generate(**input, max_new_tokens=300, do_sample=False)
        summary = tokenizer.decode(output[0], skip_special_tokens=True)
        chunk_summaries.append(summary)

    return ' '.join(chunk_summaries)


def already_summarized(project_id, extracted_file_name):
    cursor = conn.cursor()
    cursor.execute('SELECT project_id FROM public.file_summary WHERE project_id = %s AND extracted_file_name = %s', (project_id, extracted_file_name))
    exists = cursor.fetchone() is not None
    cursor.close()
    return exists


def save_project(project_id, summarizations, summary_of_summaries):
    cursor = conn.cursor()

    for summary in summarizations:
        proj_folder = os.path.join('../APIScraper/downloads', project_id)
        file_path = ''

        file_name_no_ext = glob.escape(summary['file_name'].replace('.txt', ''))

        pattern = os.path.join(proj_folder, f'{file_name_no_ext}.*')

        for infile in glob.glob(pattern):
            file_path = infile
            break

        original_file_name = os.path.basename(file_path)
        extracted_file_name = summary['file_name']

        file_text = summary['file_text']
        summary_text = summary['summary_text']

        with open(file_path, 'rb') as f:
            ba = f.read()
            cursor.execute("INSERT INTO public.file_summary (summary_text, project_id, original_file_name, file_text, file_binary, extracted_file_name) VALUES (%s, %s, %s, %s, %s, %s)",
                   (summary_text, project_id, original_file_name, file_text, ba, extracted_file_name))
            
    cursor.execute("INSERT INTO public.project_summary (project_id, summary_text) VALUES (%s, %s)", (project_id, summary_of_summaries))

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
        print('Summarizing summaries...')
        summary_texts = [summary['summary_text'] for summary in summarizations]
        summary_of_summaries = summarize(' '.join(summary_texts))

        save_project(project_id, summarizations, summary_of_summaries)

    summarizations = []
    

