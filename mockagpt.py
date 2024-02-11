from openai import OpenAI
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
import json
import csv


# constants
csv_file = "response.csv"
model = "gpt-4-turbo-preview"  # gpt-4-turbo-preview currently points to gpt-4-0125-preview as of 2024-02-03, and it *probably* has a maximum output of 4,096 tokens
number_of_rows = 3
columns = ["Movie Name", "Movie Description", "Movie Genre", "Release Date"]
prompt = [
    {
        "role": "system",
        "content": """
        You are a software developer's assistant helping to generate test data to be imported to a database. 
        You will be provided with 2 things: number of rows and the list of columns.
        Your response must be provided in JSON format where each column name is a key.
        All keys must be grouped under a single parent key called "response".
        Be creative and really vary your responses, aim to be fictional and try to avoid real world references. 
        If the column is a category like Movie Genre, you can list multiple categories -- try to vary the amount of categories in the list.
        If the column is an ID, it must increase incrementally starting from 1 -- e.g. 1, 2, 3, 4.
        If the column is a date, it should be in yyyy-mm-dd format
      """,
    },
    {
        "role": "user",
        "content": f"Generate {number_of_rows} rows for the following columns: {columns}",
    },
]


def callChatGpt(client, model, prompt, presence_penalty=0.2, temperature=1.2):
    completion = client.chat.completions.create(
        model=f"{model}",
        messages=prompt,
        response_format={"type": "json_object"},
        presence_penalty=presence_penalty,  # promotes variety, as opposed to frequency_penalty which reduces repetition and tends to cause issues with formatting, default = 0
        temperature=temperature,  # lower values -> more deterministic, higher values -> more random, default = 1
    )
    return completion


# loads .env file, OpenAI() by defaults checks for "OPENAI_API_KEY"
load_dotenv()
client = OpenAI()
completion = callChatGpt(client, model, prompt)

# parse the response and save as csv for importing to mysql workbench
response = json.loads(completion.choices[0].message.content.strip())["response"]

# use keys from first element as column names, then fill in the rows
with open(csv_file, mode="w") as file:
    for i, row in enumerate(response, start=1):
        row["ID"] = i
    writer = csv.DictWriter(file, fieldnames=response[0].keys())
    writer.writeheader()
    writer.writerows(response)