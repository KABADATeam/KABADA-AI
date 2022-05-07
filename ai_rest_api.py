import argparse
import json
import os
import sys

from flask import Flask, request
from collections import defaultdict
from BayesNetwork import MultiNetwork
from Translator import Translator, Flattener
from gevent.pywsgi import WSGIServer
from config import repo_dir, log_dir, path_pid, path_ip_port_json
import logging


app = Flask(__name__)


logging.basicConfig(
    filename=log_dir + "/app.log",
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# file_handler = logging.FileHandler(log_dir + "/app.log")
# file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
# file_handler.setLevel(logging.DEBUG)

dict_sessions = {}
translator = Translator()
flattener = Flattener()
mbn = MultiNetwork(translator=translator, flattener=flattener)

@app.route('/predict', methods=['POST'])
def predict():
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        json = request.json

        location = json["location"]
        id_bp = json['plan']['businessPlan_id']
        logging.info(f"received business plan with id {id_bp}")

        guids_by_bn = flattener(json, flag_generate_plus_one=True)

        logging.info('received num %s bns idetified', len(guids_by_bn))

        recomendations_by_bn = mbn.predict_all(guids_by_bn)

        bp = flattener.back(recomendations_by_bn)

        bp['location'] = location
        bp['plan']['businessPlan_id'] = id_bp
        logging.info(f"processing successfull of business plan with id {id_bp}")
        return bp
    else:
        return 'Content-Type not supported!'


@app.route('/learn', methods=['POST'])
def learn():
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        logging.info('receive_status == success')
        json = request.json

        # id_session = json['plan']['learningSessionId']
        # is_first = json['plan']['isFirst']
        # is_last = json['plan']['isLast']
        # logging.info(f"id_session={id_session}, is_first={is_first}, is_last={is_last}")
        return {'receive_status': 'success'}
    else:
        logging.info('receive_status == failed')
        return {'receive_status': 'failed'}


if __name__ == "__main__":

    if os.path.exists(path_pid):
        print("pid file exists, daemon already running, if not - delete pid file")
        sys.exit(1)

    with open(path_pid, "w") as conn:
        conn.write(str(os.getpid()))

    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', type=str, default="localhost")
    parser.add_argument('--port', type=int, default="2222")
    args = parser.parse_args()

    if os.path.exists(path_ip_port_json):
        with open(path_ip_port_json, "r") as conn:
            ip_port = json.load(conn)
            if "ip" in ip_port:
                args.ip = ip_port['ip']
            if "port" in ip_port:
                args.port = int(ip_port['port'])

    # app.run(args.ip, args.port)
    http_server = WSGIServer((args.ip, args.port), app, log=None, error_log=None)
    http_server.serve_forever()