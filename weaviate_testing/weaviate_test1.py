import os
import json
import openai
import weaviate
import requests
from dotenv import load_dotenv

load_dotenv()

# OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")




client = weaviate.Client(
    url = "https://repotopdf-5nn382pn.weaviate.network",  # Replace with your endpoint
    auth_client_secret=weaviate.AuthApiKey(api_key="KgxwUxGHKMT0T3Y27iiygBLDpiBi1hyMYkTV"),  # Replace w/ your Weaviate instance API key
    additional_headers = {
        "X-OpenAI-Api-Key": "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"  # Replace with your inference API key
    }
)

class_obj = {
    "class": "newnewQuestion",
    "vectorizer": "text2vec-openai",  # If set to "none" you must always provide vectors yourself. Could be any other "text2vec-*" also.
    "moduleConfig": {
        "text2vec-openai": {},
        "generative-openai": {}  # Ensure the `generative-openai` module is used for generative queries
    }
}

client.schema.create_class(class_obj)


resp = requests.get('https://raw.githubusercontent.com/weaviate-tutorials/quickstart/main/data/jeopardy_tiny.json')
data = json.loads(resp.text)  # Load data

client.batch.configure(batch_size=100)  # Configure batch
with client.batch as batch:  # Initialize a batch process
    for i, d in enumerate(data):  # Batch import data
        print(f"importing question: {i+1}")
        properties = {
            "answer": d["Answer"],
            "question": d["Question"],
            "category": d["Category"],
        }
        batch.add_data_object(
            data_object=properties,
            class_name="Question"
        )