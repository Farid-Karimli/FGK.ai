import pandas as pd

questions_list = open("data/questions.txt", "r").readlines()
questions_list = [line.strip() for line in questions_list]

df = pd.DataFrame(columns=["question", "answer"])

for question in questions_list:
    answer = input(question + "\n")
    df = df._append({"question": question, "answer": answer}, ignore_index=True)

df.to_csv("data/answers.csv", index=False)
