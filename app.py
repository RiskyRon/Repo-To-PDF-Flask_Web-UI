from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
from pdf_scripts import semantic_search
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration for file uploads
UPLOAD_FOLDER = 'dropzone'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to check if the uploaded file is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_query = request.form['message']
    response = semantic_search.get_response(user_query)
    return jsonify(response=response)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify(error="No file part")
    file = request.files['file']
    if file.filename == '':
        return jsonify(error="No selected file")
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify(success=True, message="File uploaded successfully")
    return jsonify(error="File type not allowed")

if __name__ == "__main__":
    app.run(debug=True)

