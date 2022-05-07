import argparse
import json
import os
import sys
from time import sleep

from flask import Flask, request
from collections import defaultdict
from BayesNetwork import MultiNetwork
from Translator import Translator, Flattener
from gevent.pywsgi import WSGIServer
import multiprocessing as mp
from config import repo_dir, log_dir, path_pid, path_ip_port_json
import logging


app = Flask(__name__)

logging.basicConfig(
    filename=log_dir + "/app.log",
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def worker_predictor(bp_queue, reco_queue):
    translator = Translator()
    flattener = Flattener()
    mbn = MultiNetwork(translator=translator, flattener=flattener)
    logging.info('MultiNetwork initialized')
    while True:
        bp = bp_queue.get()
        guids_by_bn = flattener(bp, flag_generate_plus_one=True)
        logging.info('received num %s bns idetified', len(guids_by_bn))
        recomendations_by_bn = mbn.predict_all(guids_by_bn)
        reco = flattener.back(recomendations_by_bn)
        reco_queue.put(reco)


def worker_input_saver(bp_save_queue):
    while True:
        if bp_save_queue.empty():
            sleep(0.1)
            continue

        # takes last input
        while not bp_save_queue.empty():
            bp = bp_save_queue.get()

        with open(log_dir + "/last_input.json", "w") as conn:
            json.dump(bp, conn)

bp_queue = mp.Queue()
bp_save_queue = mp.Queue()
reco_queue = mp.Queue()

@app.route('/predict', methods=['POST'])
def predict():
    global processes
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        bp = request.json

        location = bp["location"]
        id_bp = bp['plan']['businessPlan_id']
        logging.info(f"received business plan with id {id_bp}")

        bp_queue.put(bp)
        bp_save_queue.put(bp)
        if not processes[0].is_alive():
            logging.error("predict process has crashed")
            for q in [reco_queue, bp_queue, bp_save_queue]:
                while not q.empty():
                    q.get()
            processes[0].start()
            logging.info("predict process restart is successful")
            return "predict failed, restarted process, try again"
        else:
            reco = reco_queue.get()
            reco['location'] = location
            reco['plan']['businessPlan_id'] = id_bp
            logging.info(f"processing successful of business plan with id {id_bp}")
            return reco

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

    processes = [
        mp.Process(target=worker_predictor, args=(bp_queue, reco_queue)),
        mp.Process(target=worker_input_saver, args=(bp_save_queue,)),
    ]
    for p in processes:
        p.daemon = True
        p.start()
    sleep(2)
    # if os.path.exists(path_pid):
    #     print("pid file exists, daemon already running, if not - delete pid file")
    #     sys.exit(1)

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

    app.run(args.ip, args.port)
    # http_server = WSGIServer((args.ip, args.port), app, log=None, error_log=None)
    # http_server.serve_forever()