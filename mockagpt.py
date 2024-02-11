from openai import OpenAI
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import csv
import math


# constants
filename = input("Please enter table name: ")
model = "gpt-4-turbo-preview"  # gpt-4-turbo-preview currently points to gpt-4-0125-preview as of 2024-02-03, and it *probably* has a maximum output of 4,096 tokens
num_rows = min(
    int(input("Please enter the number of rows to be generated (max. 1000): ")), 1000
)
columns = [
    item.strip()
    for item in input(
        "Please enter a list of columns, separated by commas (e.g. Name, Description, Genre, Release Date): "
    ).split(",")
]
context = input("Please provide additional instructions or context, if any: ")
presence_penalty = 0.1
temperature = 1.1
max_rows_per_thread = 10 # from testing, using movie name/genre/description/release_date, most I can do is ~40 rows per call


def callChatGpt(client, model, num_rows, columns, presence_penalty, temperature):
    completion = client.chat.completions.create(
        model=f"{model}",
        messages=[
            {
                "role": "system",
                "content": """You are a software developer's assistant helping to generate test data to be imported to a database. 
                          You will be provided with 2 things: number of rows and the list of columns.
                          Your response must be provided in JSON format where each column name is a key.
                          All keys must be grouped under a single parent key called "response".
                          Be creative and really vary your responses, aim to be fictional and try to avoid real world references (parodies are okay). 
                          If the column is a category like Movie Genre, you can list multiple categories in the format of ['category 1', 'category 2', 'category 3', and so on] -- try to vary the amount of categories in the list.
                          If the column is an ID, it must increase incrementally starting from 1 -- e.g. 1, 2, 3, 4.
                          If the column is a date, it should be in yyyy-mm-dd format. Year can range from 1950 to current year. Other column values must be appropriate for the year provided."""
            },
            {
                "role": "user",
                "content": f"Generate '{num_rows}' rows for a '{filename}' table with the following columns: '{columns}'. {context}",
            },
        ],
        response_format={"type": "json_object"},
        presence_penalty=presence_penalty,  # promotes variety, as opposed to frequency_penalty which reduces repetition, default = 0, may cause formatting issues
        temperature=temperature,  # lower values -> more deterministic, higher values -> more random, default = 1, may cause formatting issues
    )
    return completion


# loads .env file, OpenAI() by defaults checks for "OPENAI_API_KEY"
load_dotenv()
client = OpenAI()

# multithread calls as it takes a long time and has output token limitations per call
response = []
num_threads = math.ceil(num_rows / max_rows_per_thread)
with ThreadPoolExecutor(max_workers=num_threads) as executor:
    futures = []
    for _ in range(num_threads):
        # calculate number of rows per thread, last thread may have less rows than max
        rows_per_current_thread = min(max_rows_per_thread, num_rows)
        num_rows -= rows_per_current_thread
        future = executor.submit(
            callChatGpt,
            client,
            model,
            rows_per_current_thread,
            columns,
            presence_penalty,
            temperature,
        )
        futures.append(future)

    # collecting results
    for future in as_completed(futures):
        response.extend(
            json.loads(future.result().choices[0].message.content.strip())["response"]
        )

# save as csv for importing to mysql workbench
# use keys from first element as column names, then fill in the rows
with open(f"{filename}.csv", mode="w") as file:
    fieldnames = ["ID"] + [
        key for key in response[0].keys()
    ]  # force ID to be first column
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    for i, row in enumerate(response, start=1):
        row["ID"] = i
    writer.writerows(response)
    print(f">>> {filename}.csv has been generated <<<")
