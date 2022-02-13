import argparse
from flask import Flask, request
from collections import defaultdict
from BayesNetwork import MultiNetwork
from Translator import Translator
from config import repo_dir
import logging

parser = argparse.ArgumentParser()
parser.add_argument('--ip', type=str, default="localhost")
parser.add_argument('--port', type=int, default="2222")

args = parser.parse_args()

app = Flask(__name__)


app.debug = True
applogger = app.logger
file_handler = logging.FileHandler(repo_dir + "/shared_files/app.log")
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
file_handler.setLevel(logging.DEBUG)
applogger.setLevel(logging.DEBUG)
applogger.addHandler(file_handler)

dict_sessions = {}
translator = Translator()

@app.route('/predict', methods=['POST'])
def predict():
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        json = request.json
        # id_session = json['id_session']
        id_session = 0
        logging.info('received %s', json['guids'])
        if id_session not in dict_sessions:
            dict_sessions[id_session] = MultiNetwork()

        translation = translator(json['guids'])
        bp = dict_sessions[id_session].predict_all(translation)
        logging.info('returning %s', json['guids'])
        return {"value": translator.back(bp), "status": "success"}
    else:
        return 'Content-Type not supported!'


app.run(args.ip, args.port)