 
# This script starts by asking user for PDF path, then derives class name from PDF file name.
# Then, it creates a new class in Weaviate with the name derived from the PDF file name.
# Then, it iterates through each page in the PDF and extracts text content from each page.
# Finally, it inserts each page into Weaviate as a document object that has been vectorised.

import os
import weaviate
import pdfplumber
from weaviate import Config
import weaviate.classes as wvc
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

client = weaviate.Client(
    "http://localhost:8080",
    additional_config=Config(grpc_port_experimental=50051),
    # ⬇️ Optional, if you want to try it with an inference API / generative search:
    additional_headers={
        "X-OpenAI-Api-Key": os.environ["OPENAI_API_KEY"],  # Replace with your key
    },
)

print(client.is_ready())  # This should print True if Weaviate is ready

def get_pdf_path():
    # List all PDFs in the 'converted_to_pdf/' directory
    pdf_dir = 'converted_to_pdf/'
    pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
    
    # Display options to the user
    print("0: Enter path to PDF")
    for i, pdf_file in enumerate(pdf_files, start=1):
        print(f"{i}: {pdf_file}")
    
    # Get user selection
    selection = input("Please enter the number of your selection: ")
    
    # Validate user selection
    if selection == '0':
        # If user selected 0, prompt for the PDF path
        pdf_path = input("Please enter the path to the PDF: ")
    elif selection.isdigit() and 1 <= int(selection) <= len(pdf_files):
        # If user selected a valid number, get the corresponding PDF path
        pdf_path = os.path.join(pdf_dir, pdf_files[int(selection) - 1])
    else:
        # If user input is invalid, prompt again
        print("Invalid selection. Please try again.")
        return get_pdf_path()  # Recursive call to prompt user again
    
    return pdf_path

# Get the PDF path from the user
pdf_path = get_pdf_path()

# Derive class name from PDF file name
class_name = Path(pdf_path).stem.lower() 

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

# Optionally, print out a confirmation message
print(f"Class '{class_name}' created successfully.")

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
        print(f'Inserted page {page_number} with UUID {document_uuid}')
