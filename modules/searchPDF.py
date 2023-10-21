# PDFsearch.py
import os
import openai
from modules.weaviate_init import weaviate_client  # Importing the initialized weaviate_client from weaviate_init.py

class PDFSearch:
    def __init__(self, weaviate_client):
        self.weaviate_client = weaviate_client

    def list_classes(self):
        schema = self.weaviate_client.schema.get()
        classes = schema['classes']
        class_list = []
        if not classes:
            return None
        for i, class_info in enumerate(classes, start=1):
            class_list.append(f"{i}. {class_info['class']}")
        return class_list

    def get_class_choice(self, choice):
        schema = self.weaviate_client.schema.get()
        class_name = schema['classes'][int(choice)-1]['class']
        return class_name

    def perform_search(self, class_name, query, limit):
        pdf_document_pages = self.weaviate_client.collection.get(class_name)
        semantic_search_result = pdf_document_pages.query.near_text(query=query, limit=limit)
        search_results = []
        for page in semantic_search_result.objects:
            title = page.properties['title']
            content = page.properties['content']
            page_number = page.properties['page_number']
            confidence_percentage = page.metadata.certainty * 100
            response_text = self.generate_response(query, title, page_number, content)
            search_results.append({
                "response_text": response_text,
                "title": title,
                "page_number": page_number,
                "content": content,
                "confidence_percentage": confidence_percentage
            })
        return search_results

    def generate_response(self, user_query, title, page_number, content):
        openai.api_key = os.environ["OPENAI_API_KEY"]
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": ("""

                        You are tasked with providing a clear, concise, and informative response to a user's query based on the information extracted from a semantic search of a PDF document. When providing code snippets, ALWAYS
                        wrap them in a code block. This will ensure that the code is formatted correctly and is easy to read.
                        The user's query and the relevant text extracted from the semantic search will be provided. Your response should first address the user's query directly in a natural language format, summarizing the key points from the provided text. Where possible you should provide step by step instructions for the user to follow to complete their task. 
                        The source PDF will be provided to the user for reference. You may use any information from the PDF to help you formulate your response.
                                               
                        """

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
                temperature=0.2,
                max_tokens=1024,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            return response['choices'][0]['message']['content'].strip()
        except Exception as e:
            return str(e)

