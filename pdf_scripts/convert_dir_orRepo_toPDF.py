import os
import re
import subprocess
from pathlib import Path
import pdfkit
from pygments import highlight
from pygments.lexers.python import PythonLexer
from pygments.formatters import HtmlFormatter

def clone_repo(git_url, clone_dir):
    try:
        subprocess.run(['git', 'clone', git_url, clone_dir], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to clone repository: {e}")
        exit()

def add_filename_comment(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                comment = f"# {file}\n"
                new_content = comment + content

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)

                print(f"Prepended filename comment to {file_path}")

            except Exception as e:
                print(f"Failed to process file {file_path}: {e}")


FILE_EXTENSIONS = ('.py', '.md', '.txt', '.json', '.yaml', '.yml', '.Dockerfile', 'docker-compose.yml, .ipynb')

def convert_py_to_pdf(directory, output_filename):
    html_string = ""
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Check if the file has one of the specified extensions
            if file.endswith(FILE_EXTENSIONS):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        print(f"Read {len(content)} characters from {file_path}")  # Verify file reading

                        # Highlight code if the file is a Python file, otherwise just include the text
                        if file.endswith('.py'):
                            highlighted_content = highlight(content, PythonLexer(), HtmlFormatter(full=True))
                        else:
                            highlighted_content = f"<pre>{content}</pre>"  # Wrap non-code text in <pre> tags for formatting

                        html_string += highlighted_content + "<div style='page-break-before: always;'></div>"
                except Exception as e:
                    print(f"Failed to read or process file {file_path}: {e}")

    print(html_string[:500])  # Check HTML string generation
    try:
        pdfkit.from_string(html_string, output_filename)
    except Exception as e:
        print(f"Failed to generate PDF: {e}")

if __name__ == "__main__":
    input_path = input("Enter the path to your directory or git repository URL: ")
    input_path = os.path.expanduser(input_path)  # Expand the tilde to the user's home directory

    if input_path.startswith("https://"):
        repo_name = input_path.rstrip('/').split('/')[-1].replace('.git', '')  # Extract repo name from URL
        repo_name = repo_name.replace('-', '_')  # Replace hyphens with underscores
        directory_name = f'{repo_name}_repo'
        clone_dir = os.path.join('cloned_repos', directory_name)  # Organize cloned repos in a 'cloned_repos' directory
        clone_repo(input_path, clone_dir)
        directory_path = clone_dir
    else:
        directory_path = input_path
        directory_name = Path(directory_path).name  # Extract directory name from path
        directory_name = re.sub(r'[^a-zA-Z0-9_]', '_', directory_name)  # Ensure valid characters in directory name

    if not os.path.exists(directory_path):
        print(f"The directory {directory_path} does not exist.")
        exit()

    add_filename_comment(directory_path)  # Call the function to add filename comments

    output_filename = f'converted_to_pdf/{directory_name}.pdf'  # Create output filename based on modified directory name
    convert_py_to_pdf(directory_path, output_filename)