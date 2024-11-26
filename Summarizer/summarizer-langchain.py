import os
import psycopg2
import glob
from transformers import pipeline
from langchain_core.prompts import PromptTemplate
from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain_community.document_transformers import EmbeddingsClusteringFilter
from langchain.chains.summarize import load_summarize_chain
from langchain_community.embeddings import HuggingFaceBgeEmbeddings

FILES_FOLDER = f'../TextExtractor/files'

conn = psycopg2.connect(database='fercsummary', host='localhost', port='5432', user='alic', password='FercSummary!')

text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=80, length_function=len, is_separator_regex=False)

model_name = 'dunzhang/stella_en_1.5B_v5'
model_kwargs = {"device": "cuda"}
encode_kwargs = {"normalize_embeddings": True}
embeddings = HuggingFaceBgeEmbeddings(model_name=model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs)

summarizer = pipeline("summarization", model="facebook/bart-large-cnn", max_length=1000, min_length=30)
    
# Initialize the Huggingface LLM wrapper
hf_llm = HuggingFacePipeline(pipeline=summarizer)


def already_summarized(project_id, extracted_file_name):
    cursor = conn.cursor()
    cursor.execute('SELECT project_id FROM public.file_summary WHERE project_id = %s AND extracted_file_name = %s', (project_id, extracted_file_name))
    exists = cursor.fetchone() is not None
    cursor.close()
    return exists


def summarize(file_text):
    filter = EmbeddingsClusteringFilter(embeddings=embeddings, num_clusters=10)

    chunks = text_splitter.split_text(file_text)
    try:
        result = filter.transform_documents(documents=chunks)
        checker_chain = load_summarize_chain(hf_llm, chain_type='stuff')
        summary = checker_chain(result)
        return summary
    except Exception as e:
        return str(e)
    



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

        summary = summarize(text)

        summarizations.append({'summary_text': summary, 'file_name': file_name, 'file_text': text })

    if len(summarizations) > 0:
        print('Summarizing summaries...')
        summary_texts = [summary['summary_text'] for summary in summarizations]

        all_summaries = ' '.join(summary_texts)

        summary_of_summaries = summarize(all_summaries)
        save_project(project_id, summarizations, summary_of_summaries)

    summarizations = []
    

