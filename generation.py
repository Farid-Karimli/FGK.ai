from openai import OpenAI
import json
import re

client = OpenAI(api_key="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")

response = client.chat.completions.create(
  model="ft:gpt-3.5-turbo-1106:boston-university::8kkN3yKE",
  messages=[
    {"role": "system", "content": "You imitate the way I talk. Your name is FGK."},
    {"role": "user", "content": "Do you like video games?"},
  ]
)

print(response.choices[0].message.content)