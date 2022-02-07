from flask import Flask, request, jsonify
# ...

app = Flask(__name__)

@app.route('/post_json', methods=['POST'])
def process_json():
    request_data = request.get_json()
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        json = request.json
        return json
    else:
        return 'Content-Type not supported!'

app.run("localhost", 2222, debug=True)