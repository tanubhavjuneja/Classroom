from bottle import Bottle, run, static_file, request, redirect, template,response
import os
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote, urlparse
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import zipfile
app = Bottle()
UPLOAD_FOLDER = 'projects/'
NOTES_FOLDER = 'notes'
WEB_FOLDER="Webpages"
def get_username_from_ip(ip_address):
    with open('Resources/user_history.txt', 'r') as file:
        lines = file.readlines()
        for line in lines:
            parts = line.strip().split(',')
            if len(parts) == 2:
                saved_ip, username = parts
                if saved_ip == ip_address:
                    return username
    return None
def sanitize_ip(ip_address):
    return re.sub(r'\W', '', ip_address)
def get_upload_folder_for_ip(ip_address, username):
    sanitized_ip = sanitize_ip(ip_address)
    sanitized_username = sanitize_ip(username)
    user_folder = f"{sanitized_ip}_{sanitized_username}"
    return os.path.join(UPLOAD_FOLDER, user_folder)
def get_project_folder(ip_address, username, project_name):
    sanitized_ip = sanitize_ip(ip_address)
    sanitized_username = sanitize_ip(username)
    sanitized_project = sanitize_ip(project_name)
    user_folder = f"{sanitized_ip}_{sanitized_username}"
    project_folder = os.path.join(UPLOAD_FOLDER, user_folder, sanitized_project)
    return project_folder
@app.route('/styles/<filename:path>')
def serve_styles(filename):
    return static_file(filename, root='styles')
@app.route('/Resources/<filename:path>')
def serve_logos(filename):
    return static_file(filename, root='Resources')
@app.route('/script/<filename:path>')
def serve_script(filename):
    return static_file(filename, root='script')
@app.route('/get_username', method='GET')
def get_username():
    ip_address = request.environ.get('REMOTE_ADDR')
    username = get_username_from_ip(ip_address)
    print(f"Getting username for IP {ip_address}: {username}")
    return {'username': username}
@app.route('/ide/open_page')
def open_page():
    ip_address = request.environ.get('REMOTE_ADDR')
    print(f"IP Address: {ip_address}")
    username = get_username_from_ip(ip_address)
    print(f"Retrieved Username: {username}")
    if username:
        page_list = get_user_pages(ip_address, username)
        return template('html/open_page.html', page_list=page_list)
    else:
        print("No username found. Redirecting to login page...")
        return redirect('/login')
def get_user_pages(ip_address, username):
    user_folder = get_upload_folder_for_ip(ip_address, username)
    all_pages = [d for d in os.listdir(user_folder) if os.path.isdir(os.path.join(user_folder, d))]
    print(all_pages)
    return [page for page in all_pages]
@app.route('/ide/add_page')
def show_add_page():
    return static_file('add_page.html', root='html')
@app.route('/ide/create_page', method='POST')
def create_page():
    page_name = request.forms.get('pageName')
    if not page_name or not page_name.isalnum():
        print("Invalid pageName")
        return redirect('/ide/add_page')
    ip_address = request.environ.get('REMOTE_ADDR')
    username = get_username_from_ip(ip_address)
    page_folder = get_project_folder(ip_address, username, page_name)
    if not os.path.exists(page_folder):
        os.makedirs(page_folder)
        default_files = {'index.html': '',
            'styles.css': '',
            'script.js': ''}
        for filename, content in default_files.items():
            with open(os.path.join(page_folder, filename), 'w') as file:
                file.write(content)
    else:
        print(f"Page '{page_name}' already exists.")
        return redirect('/ide/add_page')
    return redirect(f'/ide?project_name={page_name}')
@app.route('/pages/<page_name>')
def view_page(page_name):
    ip_address = request.environ.get('REMOTE_ADDR')
    username = get_username_from_ip(ip_address)
    if username:
        project_folder = get_project_folder(ip_address, username, page_name)
        if os.path.exists(project_folder):
            combined_code = combine_code(project_folder)
            response.content_type = 'text/html; charset=utf-8'
            response.body = combined_code
            return response
        else:
            return f"Page '{page_name}' not found."
    else:
        print("No username found. Redirecting to login page...")
        return redirect('/login')
@app.route('/ide')
def ide():
    ip_address = request.environ.get('REMOTE_ADDR')
    print(f"IP Address: {ip_address}")
    username = get_username_from_ip(ip_address)
    print(f"Retrieved Username: {username}")
    if username:
        project_name = request.query.get('project_name')
        if not project_name:
            return redirect('/ide?project_name=Homepage')
        project_folder = get_project_folder(ip_address, username, project_name)
        print(f"Project folder: {project_folder}")
        if not os.path.exists(project_folder):
            os.makedirs(project_folder)
            default_files = {'index.html': '',
                'styles.css': '',
                'script.js': ''}
            for filename, content in default_files.items():
                with open(os.path.join(project_folder, filename), 'w') as file:
                    file.write(content)
        return template('html/ide.html', html_code='', project_folder=project_folder)
    else:
        print("No username found. Redirecting to login page...")
        return redirect('/login')
@app.route('/render', method='GET')
def render_combined_code():
    ip_address = request.environ.get('REMOTE_ADDR')
    username = get_username_from_ip(ip_address)
    project_name = request.query.get('project_name', 'Homepage')
    project_folder = get_project_folder(ip_address, username, project_name)
    combined_code = combine_code(project_folder)
    print(f"Combined code for project {project_name}:\n{combined_code}")
    return combined_code
def combine_code(project_folder):
    html_code = read_code_from_file(os.path.join(project_folder, 'index.html'))
    css_code = read_code_from_file(os.path.join(project_folder, 'styles.css'))
    js_code = read_code_from_file(os.path.join(project_folder, 'script.js'))
    combined_code = f"{html_code}\n<style>{css_code}</style>\n<script>{js_code}</script>"
    print(f"Combined code:\n{combined_code}")
    return combined_code
def read_code_from_file(filename):
    try:
        with open(filename, 'r') as file:
            code = file.read()
        print(f"Read code from file {filename}:\n{code}")
        return code
    except FileNotFoundError:
        print(f"File {filename} not found")
        return ''
@app.route('/study_material')
def study_material():
    ip_address = request.environ.get('REMOTE_ADDR')
    print(f"IP Address: {ip_address}")
    username = get_username_from_ip(ip_address)
    print(f"Retrieved Username: {username}")
    if username:
        print("Username exists. Redirecting to main page...")
        return static_file('study_material.html', root='html')
    else:
        print("No username found. Redirecting to login page...")
        return redirect('/login')
@app.route('/webscraper')
def webscraper():
    if not os.path.exists(WEB_FOLDER):
        os.makedirs(WEB_FOLDER)
    print(f"Created or verified existence of folder {WEB_FOLDER}")
    ip_address = request.environ.get('REMOTE_ADDR')
    print(f"IP Address: {ip_address}")
    username = get_username_from_ip(ip_address)
    print(f"Retrieved Username: {username}")
    if username:
        print("Username exists. Redirecting to main page...")
        return static_file('webscraper.html', root='html')
    else:
        print("No username found. Redirecting to login page...")
        return redirect('/login')
@app.route('/scrape', method='POST')
def scrape_webpage():
    url = request.forms.get('url')
    domain_name = urlparse(url).hostname
    output_folder = os.path.join(WEB_FOLDER,domain_name)
    if os.path.exists(output_folder):
        return f"Scraping for {url} already performed. Output folder exists at {output_folder}"
    os.makedirs(output_folder, exist_ok=True)
    try:
        html_content = get_html_with_selenium(url)
        if html_content:
            soup = BeautifulSoup(html_content, 'html.parser')
            resource_tags = soup.find_all(['link', 'script', 'img'])
            total_resources = len(resource_tags)
            count = {'downloaded': 0}
            for tag in resource_tags:
                resource_url = tag.get('href') or tag.get('src')
                if resource_url:
                    local_file_path = download_and_save_resource(url, resource_url, output_folder, count)
                    if local_file_path:
                        tag['href'] = tag['src'] = local_file_path
            html_output_path = os.path.join(output_folder, "index.html")
            with open(html_output_path, 'w', encoding='utf-8') as html_file:
                html_file.write(str(soup))
            print(f"HTML content and resources saved to {html_output_path}")
            percentage_recreated = (count['downloaded']/ total_resources) * 100
            print(f"Successfully read {percentage_recreated:.2f}% of the webpage.")
        else:
            print(f"Failed to retrieve content from {url}")
    except Exception as e:
        print(f"Error: {e}. Enter a valid URL.")
    return f"Scraping URL: {url}"
def download_and_save_resource(base_url, resource_url, output_folder, count):
    full_url = urljoin(base_url, resource_url)
    try:
        response = requests.get(full_url, timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error downloading resource {full_url}: {e}")
        return None
    filename = sanitize_filename(full_url)
    output_folder = output_folder.rstrip(os.path.sep)  
    resource_path = os.path.join(output_folder, filename)
    os.makedirs(os.path.dirname(resource_path), exist_ok=True)
    with open(resource_path, 'wb') as file:
        file.write(response.content)
    print(f"Resource saved: {resource_path}")
    count['downloaded'] += 1
    return os.path.relpath(resource_path, output_folder).replace("\\", "/")
def get_html_with_selenium(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get(url)
        time.sleep(2)
        return driver.page_source
    finally:
        driver.quit()
def is_inline_data_url(url):
    return url.startswith('data:')
def sanitize_filename(url):
    if is_inline_data_url(url):
        content_type, _ = url.split(';')
        _, extension = content_type.split('/')
        filename = f"inline_data.{extension}"
    else:
        filename = ''.join(c if c.isalnum() or c in {'_', '.'} else '_' for c in unquote(url))
        filename = filename[:255]
    return filename
@app.route('/')
def index():
    ip_address = request.environ.get('REMOTE_ADDR')
    print(f"IP Address: {ip_address}")
    username = get_username_from_ip(ip_address)
    print(f"Retrieved Username: {username}")
    if username:
        print("Username exists. Redirecting to main page...")
        return static_file('index.html', root='html')
    else:
        print("No username found. Redirecting to login page...")
        return redirect('/login')
@app.route('/login')
def login():
    ip_address = request.environ.get('REMOTE_ADDR')
    username = get_username_from_ip(ip_address)
    if username:
        return redirect('/')
    else:
        print("No username found. Redirecting to login page...")
        return static_file('username.html', root='html')
@app.route('/save_username', method='POST')
def save_username():
    ip_address = request.environ.get('REMOTE_ADDR')
    username = request.forms.get('username').strip()
    if get_username_from_ip(ip_address) == username:
        print(f"Username {username} already exists for IP address {ip_address}")
        return redirect('/')
    with open('Resources/user_history.txt', 'a') as file:
        file.write(f"{ip_address},{username}\n")
    print(f"Saved username {username} for IP address {ip_address}")
    return redirect('/')
@app.route('/favicon.ico')
def favicon():
    return static_file('favicon.ico', root='Resources')
@app.route('/save', method='POST')
def save():
    language = request.forms.get('language')
    code = request.forms.get('code')
    ip_address = request.environ.get('REMOTE_ADDR')
    username = get_username_from_ip(ip_address)
    project_name = request.query.get('project_name') 
    project_folder = get_project_folder(ip_address, username, project_name)
    filename = os.path.join(project_folder, get_filename(language))
    with open(filename, 'w') as file:
        file.write(code)
    print(f"Saved code for {language} in project {project_name} for user {username} with IP {ip_address}")
    return 'OK'
@app.route('/load', method='GET')
def load():
    language = request.query.get('language')
    ip_address = request.environ.get('REMOTE_ADDR')
    username = get_username_from_ip(ip_address)
    project_name = request.query.get('project_name')
    project_folder = get_project_folder(ip_address, username, project_name)
    filename = os.path.join(project_folder, get_filename(language))
    try:
        with open(filename, 'r') as file:
            code = file.read()
    except FileNotFoundError:
        code = ''
    print(f"Loaded code for {language} in project {project_name} for user {username} with IP {ip_address}")
    return code
def get_filename(language):
    filename_mapping = {
        'html': 'index.html',
        'css': 'styles.css',
        'js': 'script.js',
    }
    return filename_mapping.get(language, 'file.txt')
@app.route('/download/<filename:path>')
def download_file(filename):
    file_path = os.path.join('Books', filename)
    print(f"Attempting to serve file: {file_path}")
    if os.path.exists(file_path):
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return static_file(file_path, root='', download=True)
    else:
        print("File not found")
        return "File not found", 404
@app.route('/notes')
def notes():
    if not os.path.exists(NOTES_FOLDER):
        os.makedirs(NOTES_FOLDER)
    print(f"Created or verified existence of folder {NOTES_FOLDER}")
    return static_file('notes.html', root='html')
@app.route('/notes/upload', method='POST')
def do_upload():
    upload = request.files.get('file')
    if upload:
        filename = os.path.join(NOTES_FOLDER, upload.filename)
        upload.save(filename)
    print(f"Uploaded file to folder {NOTES_FOLDER}")
    return redirect('/notes')
@app.route('/notes/uploads/<filename:path>')
def serve_static(filename):
    file_path = os.path.join(NOTES_FOLDER, filename)
    if os.path.exists(file_path):
        print(f"Serving static file: {file_path}")
        return static_file(filename, root=NOTES_FOLDER)
    else:
        print("File not found")
        return "File not found", 404
@app.route('/notes/history')
def history():
    files = os.listdir(NOTES_FOLDER)
    download_links = []
    for file_name in files:
        file_path = os.path.join(NOTES_FOLDER, file_name)
        download_links.append({
            'name': file_name,
            'path': f'/notes/uploads/{file_name}',
            'download_path': f'/notes/download/{file_name}'
        })
    print(f"Listed files in folder {NOTES_FOLDER}: {download_links}")
    return template('html/history.html', files=download_links)
@app.route('/webscraper/history')
def web_history():
    files = os.listdir(WEB_FOLDER)
    download_links = []
    for file_name in files:
        file_path = os.path.join(WEB_FOLDER, file_name)
        download_links.append({
            'name': file_name,
            'download_path': f'/webscraper/download/{file_name}'
        })
    print(f"Listed files in folder {WEB_FOLDER}: {download_links}")
    return template('html/web_history.html', files=download_links)
@app.route('/webscraper/download/<filename:path>')
def download_web_file(filename):
    folder_path = os.path.join(WEB_FOLDER, filename)
    zip_file_path = f'zip/{filename}.zip'
    if not os.path.exists(folder_path):
        return "File not found", 404
    try:
        with zipfile.ZipFile(zip_file_path, 'x') as zipf:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, folder_path)
                    zipf.write(file_path, arcname=arcname)
    except FileExistsError:
        print(f"ZIP file already exists: {zip_file_path}")
    print(f"Attempting to serve file: {zip_file_path}")
    return static_file(zip_file_path, root='.', download=True)
@app.route('/notes/download/<filename:path>')
def download_file(filename):
    file_path = os.path.join(NOTES_FOLDER, filename)
    if os.path.exists(file_path):
        print(f"Attempting to serve file: {file_path}")
        return static_file(filename, root=NOTES_FOLDER, download=True)
    else:
        print("File not found")
        return "File not found", 404
@app.route('/chat')
def chat():
    ip_address = request.environ.get('REMOTE_ADDR')
    print(f"IP Address: {ip_address}") 
    username = get_username_from_ip(ip_address)
    print(f"Retrieved Username: {username}") 
    if username:
        print("Username exists. Redirecting to main chat page...") 
        return static_file('chat.html', root='html')
    else:
        print("No username found. Redirecting to login page...") 
        return redirect('/login')
@app.route('/chat/send', method='POST')
def send():
    message = request.forms.get('message')
    ip_address = request.environ.get('REMOTE_ADDR')
    username = get_username_from_ip(ip_address)
    if not username:
        return "Username required"
    with open('Resources/chat_history.txt', 'a') as file:
        file.write(f"{ip_address} ({username}): {message}\n")
    print("Message received and recorded in Resources/chat_history.txt")
    return "Message received"
@app.route('/chat/receive')
def receive():
    global messages,messageList
    ip_address = request.environ.get('REMOTE_ADDR')
    with open('Resources/chat_history.txt', 'r') as file:
        messages = file.readlines()
    messageIndex=messageDict[ip_address][1]
    messageList=len(messages)
    messageDict[ip_address][0]=messageIndex
    messageDict[ip_address][1]=len(messages)
    print(f"Read chat messages: {messages[messageIndex:messageList]}")
    return {'messages': messages[messageIndex:messageList]}
@app.route('/chat/load_chat')
def load_chat():
    global messages
    ip_address = request.environ.get('REMOTE_ADDR')
    with open('Resources/chat_history.txt', 'r') as file:
        messages = file.readlines()
    messageDict[ip_address]=[0,len(messages)]
    print(f"Read chat messages: {messages}")
    return {'messages': messages}
def get_file_list(directory):
    try:
        files = os.listdir(directory)
        return [f for f in files if os.path.isfile(os.path.join(directory, f))]
    except Exception as e:
        print(f"Error listing files in {directory}: {e}")
        return []
def start_server():
    run(app, host='0.0.0.0', port=80, debug=True)
if __name__ == '__main__':
    messageDict={'0.0.0.0':[0,0]}
    if not os.path.exists('Resources/chat_history.txt'):
        with open('Resources/chat_history.txt', 'w') as file:
            pass
    if not os.path.exists('Resources/user_history.txt'):
        with open('Resources/user_history.txt', 'w') as file:
            pass
    start_server()