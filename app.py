from flask import Flask, request, jsonify
from collections import defaultdict
from BayesNetwork import MultiNetwork
from Translator import Translator

app = Flask(__name__)

dict_sessions = {}
translator = Translator()


@app.route('/predict', methods=['POST'])
def predict():
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        json = request.json
        id_session = json['id_session']
        if id_session not in dict_sessions:
            dict_sessions[id_session] = MultiNetwork()

        translation = translator(json['body_json'])
        bp = dict_sessions[id_session].predict_all(translation)

        return {"value": translator.back(bp), "status": "success"}
    else:
        return 'Content-Type not supported!'


app.run("localhost", 2222, debug=True)