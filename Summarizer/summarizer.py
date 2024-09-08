from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import os
import nltk

nltk.download('punkt')
nltk.download('punkt_tab')

PROJECT_ID = 'P-1025'

FOLDER = f'../TextExtractor/files/{PROJECT_ID}'

MODEL = 'philschmid/bart-large-cnn-samsum'

tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL)


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


summarizations = []

for file_name in os.listdir(FOLDER):
    path = os.path.join(FOLDER, file_name)

    with open(path, 'r') as file:
        text = file.read().strip()

    summary = summarize(text)
    summarizations.append(summary)
    

summary_of_summaries = summarize(' '.join(summarizations))

summaries_dir = 'summaries'
if not os.path.exists(summaries_dir):
    os.mkdir(summaries_dir)

summary_path = os.path.join(summaries_dir, PROJECT_ID + '.txt')

with open(summary_path, 'w') as f:
    f.write('\n\n'.join(summarizations))
    f.write('\n\n\nConclusion:\n')
    f.write(summary_of_summaries)