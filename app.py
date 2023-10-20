#app.py
from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
from modules.searchPDF import PDFSearch
from modules import vectorise
from modules.weaviate_init import weaviate_client
from werkzeug.utils import secure_filename

app = Flask(__name__)
print(f'############GPT-3.5-turbo in use for development.##################')

# Configuration for file uploads
UPLOAD_FOLDER = 'dropzone'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
pdf_search = PDFSearch(weaviate_client)


# Function to check if the uploaded file is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_client():
    # Replace with your Weaviate instance details
    return weaviate_client()

def delete_class_from_weaviate(class_name):
    try:
        weaviate_client.schema.delete_class(class_name)
        print(f"Class {class_name} deleted successfully.")  # Add logging
        return True
    except Exception as e:
        print(f"Failed to delete class '{class_name}': {e}")
        return False


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get-classes', methods=['GET'])
def get_classes():
    class_list = pdf_search.list_classes()
    return jsonify(class_list=class_list)


@app.route('/search', methods=['POST'])
def perform_search():
    class_choice = request.form.get('class_choice')
    query = request.form.get('query')
    page_limit = int(request.form.get('page_limit', 1))
    class_name = pdf_search.get_class_choice(class_choice)
    results = pdf_search.perform_search(class_name, query, page_limit)
    #print(f"Request Data: {request.form}") #used for debugging
    #print(f"Response Data: {results}")     #used for debugging
    return jsonify(results)


@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file', None)
    
    if not file or file.filename == '':
        return jsonify(error="No selected file or no file part")
    
    if allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        vectorise.vectorize_and_delete_pdfs_from_folder()
        return jsonify(success=True, message="File uploaded and vectorized successfully")
    
    return jsonify(error="File type not allowed")

@app.route('/delete-class', methods=['POST'])
def delete_class():
    class_name = request.form.get('class_name')
    if not class_name:
        return jsonify(success=False, error='No class name provided.')
    
    success = delete_class_from_weaviate(class_name)
    print(f'Deletion of {class_name} successful: {success}')
    return jsonify(success=success)

if __name__ == "__main__":
    app.run(debug=True)