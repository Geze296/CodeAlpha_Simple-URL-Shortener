from flask import Flask, request, redirect, render_template, url_for
import sqlite3
import string
import random
import os

app = Flask(__name__)
DB_FILE = 'url_shortener.db'

# Initialize DB
def init_db():
    if not os.path.exists(DB_FILE):
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute('CREATE TABLE urls (id INTEGER PRIMARY KEY, short TEXT UNIQUE, original TEXT)')
init_db()

# Generate a random short code
def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# Home with simple form
@app.route('/', methods=['GET', 'POST'])
def index():
    short_url = None
    if request.method == 'POST':
        original_url = request.form['url']
        short_code = generate_short_code()
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute('INSERT INTO urls (short, original) VALUES (?, ?)', (short_code, original_url))
        short_url = request.host_url + short_code
    return render_template('index.html', short_url=short_url)

# API: Shorten a long URL
@app.route('/api/shorten', methods=['POST'])
def api_shorten():
    data = request.json
    original_url = data.get('url')
    if not original_url:
        return {'error': 'Missing URL'}, 400
    short_code = generate_short_code()
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('INSERT INTO urls (short, original) VALUES (?, ?)', (short_code, original_url))
    return {'short_url': request.host_url + short_code}

# Redirect short URL to original
@app.route('/<short_code>')
def redirect_to_original(short_code):
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.execute('SELECT original FROM urls WHERE short = ?', (short_code,))
        row = cur.fetchone()
    if row:
        return redirect(row[0])
    else:
        return 'URL not found', 404

if __name__ == '__main__':
    app.run(debug=True)