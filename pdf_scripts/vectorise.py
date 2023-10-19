#vectorise.py
import os
import weaviate
import pdfplumber
from weaviate import Config
import weaviate.classes as wvc
from weaviate_init import client

from pathlib import Path

UPLOAD_FOLDER = "dropzone"  

def vectorize_and_delete_pdfs_from_folder():
    # Check if Weaviate is ready
    if not client.is_ready():
        raise Exception("Weaviate is not ready!")

    # List all PDFs in the UPLOAD_FOLDER
    pdf_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.pdf')]

    # Check if there are any PDFs to process
    if not pdf_files:
        print("No PDFs found in the UPLOAD_FOLDER.")
        return

    for pdf_file in pdf_files:
        pdf_path = os.path.join(UPLOAD_FOLDER, pdf_file)

        # Derive class name from PDF file name
        class_name = Path(pdf_path).stem.lower()

        # Create a class in Weaviate for the PDF
        articles = client.collection.create(
            name=class_name,
            properties=[
                wvc.Property(
                    name="title",
                    data_type=wvc.DataType.TEXT,
                ),
                wvc.Property(
                    name="content",
                    data_type=wvc.DataType.TEXT,
                ),
                wvc.Property(
                    name="page_number",
                    data_type=wvc.DataType.INT,
                ),
            ],
            vectorizer_config=wvc.ConfigFactory.Vectorizer.text2vec_openai()
        )

        # Get the created class from Weaviate
        pdf_document_pages = client.collection.get(class_name)

        # Open the specified PDF file
        with pdfplumber.open(pdf_path) as pdf:
            # Iterate through each page in the PDF
            for page_number, page in enumerate(pdf.pages, start=1):
                # Extract text content from the page
                text_content = page.extract_text()
                # Create a document object with the extracted data
                document = {
                    "title": f"{class_name} - Page {page_number}",
                    "content": text_content,
                    "page_number": page_number
                }
                # Insert the document object into Weaviate
                document_uuid = pdf_document_pages.data.insert(document)
                print(f'Inserted page {page_number} of {pdf_file} with UUID {document_uuid}')

        # Delete the processed PDF
        os.remove(pdf_path)

    return class_name

# Test the function
if __name__ == "__main__":
    vectorize_and_delete_pdfs_from_folder()
