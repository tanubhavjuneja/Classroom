from bottle import Bottle, run, static_file, request, redirect, template
import os
import re
app = Bottle()
UPLOAD_FOLDER = 'projects/'
NOTES_FOLDER = 'notes'
def get_username_from_ip(ip_address):
    with open('user_history.txt', 'r') as file:
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
@app.route('/script/<filename:path>')
def serve_script(filename):
    return static_file(filename, root='script')
@app.route('/get_username', method='GET')
def get_username():
    ip_address = request.environ.get('REMOTE_ADDR')
    username = get_username_from_ip(ip_address)
    print(f"Getting username for IP {ip_address}: {username}")
    return {'username': username}
@app.route('/ide')
def ide():
    ip_address = request.environ.get('REMOTE_ADDR')
    print(f"IP Address: {ip_address}")
    username = get_username_from_ip(ip_address)
    print(f"Retrieved Username: {username}")
    if username:
        project_name = request.query.get('project_name', 'default')
        project_folder = get_project_folder(ip_address, username, project_name)
        print(f"Project folder: {project_folder}")
        if not os.path.exists(project_folder):
            os.makedirs(project_folder)
            default_files = {
                'index.html': '<!DOCTYPE html>\n<html>\n<head>\n  <link rel="stylesheet" type="text/css" href="styles.css">\n</head>\n<body>\n  <script src="script.js"></script>\n</body>\n</html>',
                'styles.css': '/* Your CSS styles here */',
                'script.js': '// Your JavaScript code here'
            }
            for filename, content in default_files.items():
                with open(os.path.join(project_folder, filename), 'w') as file:
                    file.write(content)

        return template('ide', html_code='', project_folder=project_folder)
    else:
        print("No username found. Redirecting to login page...")
        return redirect('/login')
@app.route('/render', method='GET')
def render_combined_code():
    ip_address = request.environ.get('REMOTE_ADDR')
    username = get_username_from_ip(ip_address)
    project_name = request.query.get('project_name', 'default')
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
        return static_file('study_material.html', root='.')
    else:
        print("No username found. Redirecting to login page...")
        return redirect('/login')
@app.route('/')
def index():
    ip_address = request.environ.get('REMOTE_ADDR')
    print(f"IP Address: {ip_address}")
    username = get_username_from_ip(ip_address)
    print(f"Retrieved Username: {username}")
    if username:
        print("Username exists. Redirecting to main page...")
        return static_file('index.html', root='.')
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
        return static_file('username.html', root='.')
@app.route('/save_username', method='POST')
def save_username():
    ip_address = request.environ.get('REMOTE_ADDR')
    username = request.forms.get('username').strip()
    if get_username_from_ip(ip_address) == username:
        print(f"Username {username} already exists for IP address {ip_address}")
        return redirect('/')
    with open('user_history.txt', 'a') as file:
        file.write(f"{ip_address},{username}\n")
    print(f"Saved username {username} for IP address {ip_address}")
    return redirect('/')
@app.route('/favicon.ico')
def favicon():
    return static_file('favicon.ico', root='./')
@app.route('/save', method='POST')
def save():
    language = request.forms.get('language')
    code = request.forms.get('code')
    ip_address = request.environ.get('REMOTE_ADDR')
    username = get_username_from_ip(ip_address)
    project_name = request.query.get('project_name', 'default')
    project_folder = get_project_folder(ip_address, username, project_name)
    if not os.path.exists(project_folder):
        os.makedirs(project_folder)
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
    project_name = request.query.get('project_name', 'default')
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
@app.route('/list_files')
def list_files():
    directory = request.query.get('dir', 'Books')
    file_list = get_file_list(directory)
    print(f"Listed files in directory {directory}: {file_list}")
    return {'files': file_list}
@app.route('/download/<filename:path>')
def download_file(filename):
    file_path = os.path.join('Books', filename)
    print(f"Attempting to serve file: {file_path}")
    if os.path.exists(file_path):
        return static_file(file_path, root='', download=True)
    else:
        print("File not found")
        return "File not found", 404
@app.route('/notes')
def notes():
    if not os.path.exists(NOTES_FOLDER):
        os.makedirs(NOTES_FOLDER)
    print(f"Created or verified existence of folder {NOTES_FOLDER}")
    return template('notes.html')
@app.route('/notes/upload', method='POST')
def do_upload():
    upload = request.files.get('file')
    if upload:
        filename = os.path.join(NOTES_FOLDER, upload.filename)
        upload.save(filename)
    print(f"Uploaded file to folder {NOTES_FOLDER}")
    return template('notes.html')
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
    return template('history.html', files=download_links)
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
        return static_file('chat.html', root='.')
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
    with open('chat_history.txt', 'a') as file:
        file.write(f"{ip_address} ({username}): {message}\n")
    print("Message received and recorded in chat_history.txt")
    return "Message received"
@app.route('/chat/receive')
def receive():
    with open('chat_history.txt', 'r') as file:
        messages = file.readlines()
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
    if not os.path.exists('chat_history.txt'):
        with open('chat_history.txt', 'w') as file:
            pass
    if not os.path.exists('user_history.txt'):
        with open('user_history.txt', 'w') as file:
            pass
    start_server()