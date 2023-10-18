# This repo can convert any Folder into a pdf, then vectorise and run semantic searches against it, it has a flask web UI

1: Clone repo

```bash
git clone https://github.com/RiskyRon/Repo-To-PDF-Flask_Web-UI.git
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


7: You are now ready to run semantic searches against the pdf with the following command by launching the flask web-UI by running

```python
python3 app.py
```
