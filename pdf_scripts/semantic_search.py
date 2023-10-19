import os
import re
import openai
import weaviate
import pdfplumber
from weaviate import Config
import weaviate.classes as wvc
from dotenv import load_dotenv

def list_classes(client):
    schema = client.schema.get()
    classes = schema['classes']
    if not classes:
        print("Please vectorise a PDF to begin searching.")
        exit()  # This will terminate the script
    for i, class_info in enumerate(classes, start=1):
        print(f"{i}. {class_info['class']}")

def get_class_choice(client):
    list_classes(client)
    choice = input("Select the number of the PDF you want to search: ")
    while not choice.isdigit() or not (1 <= int(choice) <= len(client.schema.get()['classes'])):
        print("Invalid choice. Please select a valid number from the list.")
        choice = input("Select the number of the PDF you want to search: ")
    schema = client.schema.get()
    class_name = schema['classes'][int(choice)-1]['class']
    return class_name

def get_user_query():
    query = input("Enter your query: ")
    return query

def get_page_limit():
    limit = input("Enter the number of pages you want to retrieve (default is 1): ")
    return int(limit) if limit else 1

import re
import time

start_time = time.time()

def generate_response(user_query, title, page_number, content):
    openai.api_key = os.getenv("OPENAI_API_KEY")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": ("""
                        You are tasked with providing a clear, concise, and informative response to a user's query based on the information extracted from a semantic search of a PDF document. ALWAYS use `````` to wrap code snippets.
                        The user's query and the relevant text extracted from the semantic search will be provided. Your response should first address the user's query directly in a natural language format, summarizing the key points from the provided text. Where possible you should provide step by step instructions for the user to follow to complete their task. Next, you should include the actual text from the semantic search as a reference.
                        f"\n\nUser Query: {user_query}\n\nSemantic Search Output:\nTitle: {title}\nPage Number: {page_number}\nContent: {content}\n\nPlease formulate your response accordingly.\n\n"
                        """
                    )
                },
                {
                    "role": "user",
                    "content": user_query
                },
                {
                    "role": "assistant",
                    "content": ""
                }
            ],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        # Extract the response from the OpenAI API call
        raw_response = response['choices'][0]['message']['content'].strip()

        # Replace content wrapped in triple backticks with <pre><code> tags
        def replace_code(match):
            code_content = match.group(1)
            return f'<pre><code>{code_content}</code></pre>'

        formatted_response = re.sub(r'```(.*?)```', replace_code, raw_response, flags=re.DOTALL)

        return formatted_response
        print("--- %s seconds ---" % (time.time() - start_time))
    except Exception as e:
        print(f"An error occurred: {e}")
        return None  # or however you want to handle errors


def perform_search(client, class_name, query, limit):
    pdf_document_pages = client.collection.get(class_name)
    semantic_search_result = pdf_document_pages.query.near_text(
        query=query,
        limit=limit
    )
    response_texts = []

    #for page in semantic_search_result.objects:
    #    print(page)  # Just for debugging purposes

    for page in semantic_search_result.objects:
        title = page.properties['title']
        content = page.properties['content']
        page_number = page.properties['page_number']
        confidence_percentage = page.metadata.certainty * 100  # Convert score to percentage

        # Call the generate_response function here
        response_text = generate_response(query, title, page_number, content)
        
        print("="*40)
        print("GPT GENERATED SUMMARY:") 
        print("-"*40)
        if response_text:
            response_texts.append(response_text)
        else:
            response_texts.append(f'Failed to generate response for {title} (Page {page_number})')
        
    return " ".join(response_texts)
    print("--- %s seconds ---" % (time.time() - start_time))


def get_response(user_query):
    load_dotenv()

    client = weaviate.Client(
        "http://localhost:8080",
        additional_config=Config(grpc_port_experimental=50051),
        additional_headers={
            "X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY"),
        },
    )

    # For simplicity, let's select the first class and set a default limit
    class_name = client.schema.get()['classes'][0]['class']
    limit = 1  # Default limit

    return perform_search(client, class_name, user_query, limit)
    print("--- %s seconds ---" % (time.time() - start_time))

if __name__ == "__main__":
    # This code will not be executed when imported by Flask
    user_query = input("Enter your query: ")
    print(get_response(user_query))
