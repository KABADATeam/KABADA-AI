import argparse
from flask import Flask, request
from collections import defaultdict
from BayesNetwork import MultiNetwork
from Translator import Translator
# import os, sys
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# from flask_script import Manager

parser = argparse.ArgumentParser()
parser.add_argument('--ip', type=str, default="localhost")
parser.add_argument('--port', type=int, default="2222")

args = parser.parse_args()

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

        translation = translator(json['guids'])
        bp = dict_sessions[id_session].predict_all(translation)

        return {"value": translator.back(bp), "status": "success"}
    else:
        return 'Content-Type not supported!'


app.run(args.ip, args.port, debug=True)