#Generative Lecture Summarizer
#Shahariar Ali Bijoy, Tamás Lukács

import os
import sys
import whisper
import openai
import jinja2
import pdfkit
import argparse
import tiktoken


openai.api_key = "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"
model_name = "gpt-3.5-turbo"
model_max_tokens = 4096

def transcribe(media_path):
    model = whisper.load_model("base")
    transcript = model.transcribe(media_path)
    return transcript["text"]

def get_summary(transcript, summary_length):
    summary_length = int(summary_length)*3 #chatbot words are about 3 times longer than normal words?
    system_prompt = f"You are a student, who creates notes about the most important information and overarching themes of the provided university lecture. The resulting notes should be {summary_length} words in length and only contain bulletpoints separated by dashes"
    print("System Prompt: \n" + system_prompt)
    completion = openai.ChatCompletion().create(
        model = "gpt-3.5-turbo",
        temperature = 0.5,
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Universtiy Lecture: \n" + transcript}
        ]
    )
    return completion.choices[0].message.content

def gererate_pdf(title, summary, p1, p2, p3, p4, p5):

    #create html list
    summary = summary.replace("-", "</li><li>")

    context = {
        'title': title,
        'summary': summary,
        'p1': p1,
        'p2': p2,
        'p3': p3,
        'p4': p4,
        'p5': p5
    }
    template_loader = jinja2.FileSystemLoader('./')
    template_env = jinja2.Environment(loader=template_loader)
    html_template = 'summary-template.html'
    template = template_env.get_template(html_template)
    output_text = template.render(context)
    pdfkit.from_string(output_text, os.path.join("results", f"summary-{title}.pdf"))

def count_tokens(text):
    encoding = tiktoken.encoding_for_model(model_name)
    tokens = encoding.encode(text)
    return len(tokens)

def main():
    parser = argparse.ArgumentParser(description='Generative Lecture Summarizer')
    parser.add_argument("title", type=str, help="The title of the lecture")
    parser.add_argument("input", type=str, help="The path to the lecture audio file or txt file containing the transcript")
    parser.add_argument("p1")
    parser.add_argument("p2")
    parser.add_argument("p3")
    parser.add_argument("p4")
    parser.add_argument("p5")
    parser.add_argument("length", type=str, help="The length of the summary in words")
    args = parser.parse_args()

    if(args.input.endswith(".txt")):
        with open(args.input, 'r') as file:
            transcript = file.read().replace('\n', '')
    else:
        print("Transcribing...")
        transcript = transcribe(args.input)
        with open(os.path.join("results", f"transcript-{args.title}.txt"), 'w') as file:
            file.write(transcript)

    token_count = count_tokens(transcript)
    if token_count > model_max_tokens:
        print(f"The provided lecture is {token_count/model_max_tokens} times longer the current model allows. Please provide a shorter lecture or change to a different model. Model relevant model limitations: GPT-3.5: up to about 25 minues of audio, GPT-4: about 3 hours of audio")
        sys.exit(1)
    
    print("Summarizing...")
    summary = get_summary(transcript, args.length)
    print("Summary: \n" + summary)
    print("Generating PDF...")
    gererate_pdf(args.title, summary, args.p1, args.p2, args.p3, args.p4, args.p5)
    print("Done!")



if __name__ == '__main__':
    main()

#TODO
# 1. try different prompt settings.
# 2. Create user interface
# 4. think about incorporating the lecture slides into the prompt.
