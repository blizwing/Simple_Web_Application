import logging
from flask import Flask, jsonify, request, render_template, redirect, url_for, send_file
import io

# ─── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ─── App setup ─────────────────────────────────────────────────────────────────
app = Flask(__name__)
items = []

# ─── Endpoints ────────────────────────────────────────────────────────────────
@app.before_request
def log_request():
    logger.info(f"{request.remote_addr} → {request.method} {request.path}")

@app.route('/')
def index():
    logger.debug("Rendering home page")
    return render_template('index.html', count=len(items))

@app.route('/api/items', methods=['GET'])
def list_items():
    logger.info("Listing items")
    return jsonify({'items': items})

@app.route('/api/items', methods=['POST'])
def add_item():
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            logger.warning("add_item called without 'name'")
            return jsonify({'error': 'Missing "name"'}), 400

        items.append(data['name'])
        logger.info(f"Item added: {data['name']} (total={len(items)})")
        return jsonify({'message': 'Added', 'items': items}), 201

    except Exception as e:
        logger.exception("Unexpected error in add_item")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/submit', methods=['GET', 'POST'])
def submit_item():
    if request.method == 'POST':
        name = request.form.get('name')
        if name:
            items.append(name)
            logger.info(f"Form item added: {name} (total={len(items)})")
            return redirect(url_for('submit_item', success=1))
        else:
            logger.warning("submit_item POST without name")
    success = request.args.get('success')
    return render_template('submit.html', success=success)

@app.route('/download')
def download():
    logger.info("File download requested")
    buf = io.BytesIO()
    buf.write(b"Sample file for download!\n")
    buf.seek(0)
    return send_file(
        buf,
        as_attachment=True,
        download_name='sample.txt',
        mimetype='text/plain'
    )

if __name__ == '__main__':
    logger.info("Starting development server on port 5000")
    app.run(threaded=True, port=5000)
