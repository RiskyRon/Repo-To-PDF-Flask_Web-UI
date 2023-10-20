# weaviate_init.py
import os
import weaviate
from weaviate import Config
from dotenv import load_dotenv

load_dotenv()

def initialize_weaviate_client():
    client = weaviate.Client(
        "http://localhost:8080",
        additional_config=Config(grpc_port_experimental=50051),
        additional_headers={
            "X-OpenAI-Api-Key": os.environ["OPENAI_API_KEY"],
        },
    )
    return client

client = initialize_weaviate_client()
