import re
from emoji import is_emoji, demojize
from openai import OpenAI
import json
import pandas as pd

API_KEY = "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"

client = OpenAI(api_key=API_KEY)

def remove_chat_metadata(input_file):

    new_str = ""

    with open(input_file, "r") as f:
        lines = f.readlines()

        for line in lines:
            cleaned = clean_line(line)
            if cleaned != '':
                new_str += cleaned + "\n"
            
    return new_str

def clean_line(line):
    date_time = r"(\[\d+\/\d+\/\d+,\s\d+:\d+:\d+\s*([AP]M)*\])" 

    cleaned = re.sub(date_time, "", line)
    cleaned = cleaned.replace(" \" ", " \\' ")
    cleaned = cleaned.replace("‎", "")
    cleaned = demojize(cleaned)
    cleaned = cleaned.split(":")

    if cleaned[0].strip() != "FGK":
        cleaned[0] = "Other"
    else:
        cleaned[0] = "Me"

    try:
        cleaned[1] = cleaned[1].strip()
        if cleaned[1].startswith("https://"):
            return ''
    except IndexError:
        return ''

    filter_out_msgs = ("image omitted","sticker omitted", "video omitted", "document omitted")
    
    if len(cleaned) > 1:
        for msg in filter_out_msgs:
            if msg in cleaned[1]:
                return ''
    
    return ":".join(cleaned)

def consolidate(clean_chat, output_filename):
        
    output = open("chats/" + output_filename, "w")
  
    if clean_chat[0].split(":")[0] == "Me":
        start = "Me"
    else:
        start = "Other"
    
    consolidated = []
    output.write(start + ": ")
    for line in clean_chat:
        if line == "":
            continue
        line = line.lower()
        if line.split(":")[0] == start:
            try:
                output.write(" ")
                output.write(line.split(":")[1]) if line.split(":")[1] != " " or line.split(":")[1] != "" else None
                consolidated.append(line)
            except IndexError:
                continue
        else:
            
            message = line.split(":")[1]
            if message != " " and message != "":
                output.write("\n")
                start = line.split(":")[0]
                output.write(start + ": ")
                output.write(message)

            consolidated.append(line)
               
    output.close()

def turn_into_json(input_file, output_file="training_data.jsonl"):

    data = {"messages": []}

    jsonl_file = open(output_file, "w")
    input_data = open(input_file, "r").readlines()

    for i in range(0,len(input_data), 2):
        data["messages"] = []

        data["messages"].append({"role": "system", "content": "You are a chatbot that talks and texts like me. My name is Farid Karimli, and your training data is from my WhatsApp chat with one of my friends. Given some prompt you will respond with a message that is similar to the messages in the chat. Most of the chat is transliterated from Russian to English, meaning text in Russian but with English letters. Also, the messages do not follow a strict format, so you will have to learn to respond to messages that are not in the same format as the training data. Finally, the messages do not have proper grammar or punctuation, so do not incorporate that into your learning. Focus on the quips and the content of my responses."})
        data["messages"].append({"role": "user", "content": input_data[i+1].split(":")[1][:-1]}) 
        data["messages"].append({"role": "assistant", "content": input_data[i].split(":")[1][:-1]})

        jsonl_file.write(json.dumps(data))
        jsonl_file.write("\n")

    jsonl_file.close()

def create_openai_file(f, name, input_format="chat"):
    if input_format == "qa":
        create_QA_jsonl(f, name)
    else:
        turn_into_json(f, name)

    training_data = open(name, "rb")
    client.files.create(file=training_data, purpose="fine-tune")
    
def turn_to_csv(filename):
    f = open(filename, "r")
    lines = f.readlines()
    f.close()

    f = open(filename[:-4] + ".tsv", "w")
    f.write("id;text\n")
    i = 0
    for line in lines:
        line = line.split(":")
        print(line)
        if len(line) > 1 and line[0] == "me" and len(line[1].split()) > 3:
            f.write(str(i) + ";" + line[1][:-1] + "\n")
        i+=1
    f.close()

def create_QA_jsonl(filename, output_filename):
    
    input_data = pd.read_csv(filename)
    jsonl_file = open(output_filename, "w")

    data = {"messages": []}

    for row in input_data.iterrows():
        data["messages"] = []

        data["messages"].append({"role": "system", "content": "You are a chatbot that talks and texts like me. My name is Farid Karimli, and your training data is from my WhatsApp chat with one of my friends. Given some prompt you will respond with a message that is similar to the messages in the chat. Most of the chat is transliterated from Russian to English, meaning text in Russian but with English letters. Also, the messages do not follow a strict format, so you will have to learn to respond to messages that are not in the same format as the training data. Finally, the messages do not have proper grammar or punctuation, so do not incorporate that into your learning. Focus on the quips and the content of my responses."})
        data["messages"].append({"role": "user", "content": row[1]["question"]}) 
        data["messages"].append({"role": "assistant", "content": row[1]["answer"]})

        jsonl_file.write(json.dumps(data))
        jsonl_file.write("\n")

    jsonl_file.close()


create_openai_file("chats/" + "ishan_consolidated.txt", "ishan_training.jsonl")