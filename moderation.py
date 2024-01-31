from openai import OpenAI
import json
client = OpenAI(api_key="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")

f = open("training_data.jsonl", "r").readlines()

final_data = open("final_chat_data.jsonl", "w")

count = 0
for line in f:
    d = json.loads(line)
    messages = d['messages']

    user = messages[1]['content']
    bot = messages[2]['content']

    response = client.moderations.create(input=bot)
    output = response.results[0]
    if output.flagged:
        count += 1
        print("Flagged", count)
        continue
    else:
        final_data.write(json.dumps(d) + "\n")



