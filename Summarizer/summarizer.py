from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import os
import nltk

nltk.download('punkt')
nltk.download('punkt_tab')

FOLDER = '../TextExtractor/files/P-1005'

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


all_summarization = ''

for file_name in os.listdir(FOLDER):
    path = os.path.join(FOLDER, file_name)

    with open(path, 'r') as file:
        text = file.read().strip()

    summarization = summarize(text)
    print(summarization)
    all_summarization += summarization

combined_summary = summarize(all_summarization)

print('\n\n\n' + combined_summary)