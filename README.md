# This repo can convert any Folder into a pdf, then vectorise and run semantic searches against it, it has a flask web UI

1: Clone repo

```bash
git clone https://github.com/RiskyRon/Repo-To-PDF-SemanticSearch.git
```
2: setup environment

```python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3: rename .env.example to .env and add your openai api key. Get your openai api key from https://platform.openai.com/account/api-keys after creating an account.

4: To initiate the Weaviate client (where the vectors will be stored), we will use Docker.  Ensure Docker is installed and running first, then run

```bash
docker compose up -d
```

"wkhtmltopdf" is required for the conversion of directories to PDF. Download link is https://wkhtmltopdf.org/downloads.html  (tested on Mac OS Big Sur 11.7.10)

5: To convert any directory to a PDF for vectorising, run the following command and when prompted, enter the directory path. eg: /path/to/directory   This will output a pdf file with the same name as the directory.

```python
python3 convert_dir_to_pdf.py
```

6: Convert the pdf to a vector by running the following command when prompted, enter the path to the newly created pdf

```python
python3 vectorise.py
```

7: You are now ready to run semantic searches against the pdf with the following command.  Type your query when prompted in the terminal, select the number of pages to have returned (default is 1) and Bobs your Uncle!  The script will return an gpt summary along with the extracted text from the pdf related to your query!

```python
python3 semantic_search.py
```
