from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import logging
from werkzeug.utils import secure_filename
from collections import Counter

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', '.docx'}
logging.basicConfig(level=logging.INFO)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    if not allowed_file(file.filename):
        return jsonify({'message': 'File type not allowed'}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    if os.path.exists(file_path):
        return jsonify({'message': 'File already exists', 'filename': filename}), 409

    file.save(file_path)
    return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 200

@app.route('/handle_duplicate', methods=['POST'])
def handle_duplicate():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400

    file = request.files['file']
    action = request.form.get('action')
    filename = request.form.get('filename')

    if not file or not action or not filename:
        return jsonify({'message': 'Missing data'}), 400

    secure_name = secure_filename(filename)
    file_path = os.path.join(UPLOAD_FOLDER, secure_name)

    if action == 'overwrite':
        file.save(file_path)
        return jsonify({'message': 'File overwritten successfully'}), 200
    elif action == 'skip':
        return jsonify({'message': 'File upload skipped'}), 200
    elif action == 'rename':
        base, ext = os.path.splitext(secure_name)
        new_filename = f"{base}_{ext}"
        new_file_path = os.path.join(UPLOAD_FOLDER, new_filename)
        file.save(new_file_path)
        return jsonify({'message': f'File uploaded with new name {new_filename}', 'filename': new_filename}), 200
    else:
        return jsonify({'message': 'Invalid action'}), 400

@app.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({'message': f'File {filename} deleted successfully'}), 200
    return jsonify({'message': 'File not found'}), 404

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/files', methods=['GET'])
def get_files():
    files = sorted(os.listdir(app.config['UPLOAD_FOLDER']))
    return jsonify([{'filename': f} for f in files])


if __name__ == '__main__':
    app.run(debug=True)

