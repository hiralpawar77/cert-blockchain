import hashlib
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from blockchain import Blockchain
app = Flask(__name__)
app.secret_key = "super_secret_certificate_key"
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
blockchain = Blockchain()
def hash_file(file_bytes):
    return hashlib.sha256(file_bytes).hexdigest()
@app.route('/')
def index():
    blocks = blockchain.get_all_blocks()
    is_valid, status_msg = blockchain.is_chain_valid()
    return render_template('index.html', blocks=blocks, is_valid=is_valid, status_msg=status_msg)
@app.route('/issue', methods=['POST'])
def issue_certificate():
    if 'cert_file' not in request.files:
        flash('No file selected!', 'error')
        return redirect(url_for('index'))
    file = request.files['cert_file']
    if file.filename == '':
        flash('No file selected!', 'error')
        return redirect(url_for('index'))
    file_bytes = file.read()
    cert_hash = hash_file(file_bytes)
    blockchain.add_certificate(cert_hash)
    flash(f'Certificate Successfully Issued! SHA-256: {cert_hash}', 'success')
    return redirect(url_for('index'))
@app.route('/verify', methods=['POST'])
def verify_certificate():
    if 'verify_file' not in request.files:
        flash('No file selected for verification!', 'error')
        return redirect(url_for('index'))
    file = request.files['verify_file']
    if file.filename == '':
        flash('No file selected!', 'error')
        return redirect(url_for('index'))
    file_bytes = file.read()
    upload_hash = hash_file(file_bytes)

    blocks = blockchain.get_all_blocks()
    found = False
    for block in blocks:
        if block.cert_hash == upload_hash:
            found = True
            break      
    if found:
        flash(f'✅ VERIFIED: Certificate is Genuine! (Hash matched block on chain)', 'success')
    else:
        flash(f'⚠️ WARNING: Invalid or Tampered Certificate! (Hash not found on chain)', 'error')
    return redirect(url_for('index'))
if __name__ == '__main__':
    app.run(debug=True, port=5000)