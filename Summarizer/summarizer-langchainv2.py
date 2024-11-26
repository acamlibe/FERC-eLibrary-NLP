import os
import psycopg2
import glob
from transformers import pipeline
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain_community.document_transformers import EmbeddingsClusteringFilter
from langchain.chains.summarize import load_summarize_chain
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFacePipeline
from langchain.schema import Document
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from langchain_huggingface.llms import HuggingFacePipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import transformers
import torch

FILES_FOLDER = f'../TextExtractor/files'

conn = psycopg2.connect(database='fercsummary', host='localhost', port='5432', user='alic', password='FercSummary!')

text_splitter = RecursiveCharacterTextSplitter(
    # Set a really small chunk size, just to show.
    chunk_size=900,
    chunk_overlap=100,
    length_function=len,
    is_separator_regex=False,
)

model_name = 'dunzhang/stella_en_1.5B_v5'
model_kwargs = {"device": "cuda"}
encode_kwargs = {"normalize_embeddings": True}
embeddings = HuggingFaceEmbeddings(model_name=model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs)
    
# Initialize the Huggingface LLM wrapper
tokenizer = AutoTokenizer.from_pretrained("suriya7/bart-finetuned-text-summarization")
model = AutoModelForSeq2SeqLM.from_pretrained("suriya7/bart-finetuned-text-summarization")

pipeline = transformers.pipeline(
    "summarization",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=1024,
    do_sample=False,
    device=0
)

hf = HuggingFacePipeline(pipeline=pipeline)

prompt_template = """Write a concise summary of the following text.:
{text}
CONCISE SUMMARY:"""
prompt = PromptTemplate.from_template(prompt_template)

refine_template = (
    "Your job is to produce a final summary\n"
    "We have provided an existing summary up to a certain point: {existing_answer}\n"
    "We have the opportunity to refine the existing summary"
    "(only if needed) with some more context below.\n"
    "------------\n"
    "{text}\n"
    "------------\n"
    "Given the new context, refine the original summary."
    "If the context isn't useful, return the original summary."
)
refine_prompt = PromptTemplate.from_template(refine_template)
chain = load_summarize_chain(
    llm=hf,
    chain_type="refine",
    question_prompt=prompt,
    refine_prompt=refine_prompt,
    return_intermediate_steps=False,
    input_key="input_documents",
    output_key="output_text",
)

def already_summarized(project_id, extracted_file_name):
    cursor = conn.cursor()
    cursor.execute('SELECT project_id FROM public.file_summary WHERE project_id = %s AND extracted_file_name = %s', (project_id, extracted_file_name))
    exists = cursor.fetchone() is not None
    cursor.close()
    return exists


def summarize(file_text):
    filter = EmbeddingsClusteringFilter(embeddings=embeddings, num_clusters=10)

    chunks = text_splitter.split_text(file_text)
    documents = [Document(page_content=chunk) for chunk in chunks]

    #result = filter.transform_documents(documents=documents)

    result = chain({"input_documents": documents}, return_only_outputs=True)
    summary_text = result['output_text']
    return summary_text
    

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
    

