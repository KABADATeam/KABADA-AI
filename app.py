from flask import Flask, request, jsonify
from collections import defaultdict
from BayesNetwork import MultiNetwork
# ...

app = Flask(__name__)

dict_sessions = {}


@app.route('/start_session', methods=['POST'])
def start_session():
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        json = request.json
        id_session = json['id_session']
        if id_session not in dict_sessions:
            dict_sessions[id_session] = MultiNetwork()
            dict_sessions[id_session].add_net(json['bn_name'])
        return {"status": "success"}
    else:
        return 'Content-Type not supported!'


@app.route('/end_session', methods=['POST'])
def end_session():
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        json = request.json
        id_session = json['id_session']
        if id_session not in dict_sessions:
            return {"status": "failed", "desc": "session doesn't exist"}
        del dict_sessions[id_session]
        return {"status": "success"}
    else:
        return 'Content-Type not supported!'


@app.route('/give_evidence', methods=['POST'])
def give_evidence():
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        json = request.json
        id_session = json['id_session']
        if id_session not in dict_sessions:
            return {"status": "failed", "desc": "session doesn't exist"}
        dict_sessions[id_session].add_evidence(json['bn_name'], json['evidence'])
        return {"status": "success"}
    else:
        return 'Content-Type not supported!'


@app.route('/delete_evidence', methods=['POST'])
def delete_evidence():
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        json = request.json
        id_session = json['id_session']
        if id_session not in dict_sessions:
            return {"status": "failed", "desc": "session doesn't exist"}
        dict_sessions[id_session].clear_evidence(json['bn_name'], json['evidence'])
        return {"status": "success"}
    else:
        return 'Content-Type not supported!'


@app.route('/predict', methods=['POST'])
def predict():
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        json = request.json
        id_session = json['id_session']
        if id_session not in dict_sessions:
            return {"status": "failed", "desc": "session doesn't exist"}
        best_val, best_prob = dict_sessions[id_session].predict(json['bn_name'], json['evidence'])
        if best_val is None:
            return {"status": "failed"}

        return {"value": best_val, "status": "success"}
    else:
        return 'Content-Type not supported!'


app.run("localhost", 2222, debug=True)