from flask import Flask, render_template, request, jsonify
from pdf_scripts import semantic_search


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_query = request.form['message']
    response = semantic_search.get_response(user_query)
    return jsonify(response=response)

if __name__ == "__main__":
    app.run(debug=True)
