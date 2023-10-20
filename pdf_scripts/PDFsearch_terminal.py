# Import necessary libraries and modules
import os
import openai
import pdfplumber
from weaviate_init import client  # Importing the initialized client from weaviate_init.py

class PDFSearch:
    def __init__(self, client):
        self.client = client

    @staticmethod
    def list_classes():
        schema = client.schema.get()
        classes = schema['classes']
        if not classes:
            print("Please vectorise a PDF to begin searching.")
            exit()
        for i, class_info in enumerate(classes, start=1):
            print(f"{i}. {class_info['class']}")

    @staticmethod
    def get_class_choice():
        PDFSearch.list_classes()
        choice = input("Select the number of the PDF you want to search: ")
        while not choice.isdigit() or not (1 <= int(choice) <= len(client.schema.get()['classes'])):
            print("Invalid choice. Please select a valid number from the list.")
            choice = input("Select the number of the PDF you want to search: ")
        schema = client.schema.get()
        class_name = schema['classes'][int(choice)-1]['class']
        return class_name

    @staticmethod
    def get_user_query():
        query = input("Enter your query: ")
        return query

    @staticmethod
    def get_page_limit():
        limit = input("Enter the number of pages you want to retrieve (default is 1): ")
        return int(limit) if limit else 1

    @staticmethod
    def generate_response(user_query, title, page_number, content):
        openai.api_key = os.environ["OPENAI_API_KEY"]
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            f"User Query: {user_query}\n"
                            f"Semantic Search Output:\nTitle: {title}\nPage Number: {page_number}\nContent: {content}\n"
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
            return response['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def perform_search(self, class_name, query, limit):
        pdf_document_pages = client.collection.get(class_name)
        semantic_search_result = pdf_document_pages.query.near_text(query=query, limit=limit)
        for page in semantic_search_result.objects:
            title = page.properties['title']
            content = page.properties['content']
            page_number = page.properties['page_number']
            confidence_percentage = page.metadata.certainty * 100
            response_text = PDFSearch.generate_response(query, title, page_number, content)
            print("="*40)
            print("GPT GENERATED SUMMARY:") 
            print("-"*40)
            if response_text:
                print(response_text)
            else:
                print(f'Failed to generate response for {title} (Page {page_number})')
            print("\n"+"-"*40)
            print(f"SOURCE MATERIAL (Confidence: {confidence_percentage:.2f}%):")
            print("-"*40)
            print(f'{title} (Page {page_number}):\n{content}')
            print("="*40 + "\n")

if __name__ == "__main__":
    pdf_search = PDFSearch(client)
    class_name = pdf_search.get_class_choice()
    query = pdf_search.get_user_query()
    limit = pdf_search.get_page_limit()
    pdf_search.perform_search(class_name, query, limit)
