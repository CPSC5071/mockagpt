from openai import OpenAI
from dotenv import load_dotenv
import json 
import csv

# constants
csv_file = "response.csv"
model = "gpt-4-turbo-preview"
number_of_rows = 50
columns = ["Movie ID", "Movie Name", "Movie Description", "Movie Genre"]

# loads .env file, OpenAI() by defaults checks for "OPENAI_API_KEY"
load_dotenv()
client = OpenAI()

# gpt-4-turbo-preview currently points to gpt-4-0125-preview as of 2024-02-03, and it *probably* has a maximum output of 4,096 tokens
# output as json so we can parse to csv for mysql workbench
completion = client.chat.completions.create(
  model = f"{model}",
  messages = [
      {"role": "system", "content": """
        You are a software developer's assistant helping to generate test data to be imported to a database. 
        The user must provide 2 things: number of rows and the list of columns.
        Your response must be provided in JSON format and must not include any other text.
        Each key in the response is the column name, and they must all be grouped under a single parent key called "response".
        If either number of rows or list of columns is not provided, ask for it. 
        Be creative with your answers, aim to be fictional and try to avoid real world references. 
        If the column is a category like Movie Genre, you can list multiple categories.
        If the column is an ID, it must match the row number (increases incrementally, starts from 1 -- e.g. 1, 2, 3).
      """},
      {"role": "user", "content": f"Generate {number_of_rows} rows for the following columns: {columns}"}
      ],
  response_format = {"type": "json_object"}
)

# parse the response and save as csv for importing to mysql workbench
response = json.loads(completion.choices[0].message.content.strip())['response']

# use keys from first element as column names, then fill in the rows
with open(csv_file, mode='w') as file: 
    writer = csv.DictWriter(file, fieldnames = response[0].keys())
    writer.writeheader()
    writer.writerows(response)