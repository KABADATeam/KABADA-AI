import argparse
import os
import sys

from flask import Flask, request
from collections import defaultdict
from BayesNetwork import MultiNetwork
from Translator import Translator, Flattener
from gevent.pywsgi import WSGIServer
from config import repo_dir, log_dir, path_pid
import logging


app = Flask(__name__)

applogger = app.logger
file_handler = logging.FileHandler(log_dir + "/app.log")
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
file_handler.setLevel(logging.DEBUG)
applogger.setLevel(logging.DEBUG)
applogger.addHandler(file_handler)

dict_sessions = {}
translator = Translator()
flattener = Flattener()

@app.route('/predict', methods=['POST'])
def predict():
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        json = request.json
        # id_session = json['id_session']
        id_session = 0

        location = json["location"]
        id_bp = json['plan']['businessPlan_id']

        if id_session not in dict_sessions:
            dict_sessions[id_session] = MultiNetwork()

        guids_by_bn = flattener(json)
        logging.info('received num %s bns idetified', len(guids_by_bn))

        recomendations_by_bn = dict_sessions[id_session].predict_all(guids_by_bn)

        bp = flattener.back(recomendations_by_bn)

        bp['location'] = location
        bp['plan']['businessPlan_id'] = id_bp

        return bp
    else:
        return 'Content-Type not supported!'


if __name__ == "__main__":
    if os.path.exists(path_pid):
        print("Allready running")
        sys.exit(0)

    with open(path_pid, "w") as conn:
        conn.write(str(os.getpid()))
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', type=str, default="localhost")
    parser.add_argument('--port', type=int, default="2222")
    args = parser.parse_args()
    log_dir
    # app.run(args.ip, args.port)
    http_server = WSGIServer((args.ip, args.port), app, log=None, error_log=None)
    http_server.serve_forever()