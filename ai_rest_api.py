import argparse
import json
import os
import sys
from time import sleep
import pickle
from datetime import datetime
from flask import Flask, request
from collections import defaultdict
from BayesNetwork import MultiNetwork
from Translator import Translator, Flattener
from Trainer import Trainer
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

tresh_yes = 0.0

translator = Translator()
flattener = Flattener()
mbn = MultiNetwork(translator=translator, flattener=flattener, tresh_yes=tresh_yes)
trainer = Trainer(mbn=mbn)
logging.info('MultiNetwork initialized')


@app.route('/predict', methods=['POST'])
def predict(bp=None):
    if bp is None:
        content_type = request.headers.get('Content-Type')
    else:
        content_type = 'application/json'

    if content_type == 'application/json':

        try:
            if bp is None:
                bp = request.json

            location = bp["location"]

            id_bp = bp['plan']['businessPlan_id']
            logging.info(f"received business plan with id {id_bp}, location = {location}")

            if location == "plan::swot":
                id_target = id_bp
            else:
                id_target = location.split("::")[-1]
                location = "::".join(location.split("::")[:-1])

            guids_by_bn = flattener(bp, flag_generate_plus_one=True)
            logging.info('received num %s bns idetified', len(guids_by_bn))
            recomendations_by_bn = mbn.predict_all(guids_by_bn, id_target=id_target)
            reco = flattener.back(recomendations_by_bn)
            if reco is None or len(reco) == 0:
                reco = {"plan": {}}
            return reco

        except Exception as e:
            now = datetime.now()
            with open(f"{log_dir}/last_input_{now}.pickle", "wb") as conn:
                pickle.dump((now, bp), conn)
            logging.error(str(e))
            mbn.__init__(translator=translator, flattener=flattener, tresh_yes=tresh_yes)
            return {f"error: {str(e)}"}

    else:
        return 'Content-Type not supported!'


@app.route('/learn', methods=['POST'])
def learn():

    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        bp = request.json
        is_first = bp['isFirst']
        is_last = bp['isLast']
        logging.info(f"is_first={is_first}, is_last={is_last}")

        id_bp = bp['plan']['businessPlan_id']
        logging.info(f"received business plan with id {id_bp}")

        guids_by_bn = flattener(bp)
        trainer.add_bp(guids_by_bn)

        if is_last:
            try:
                logging.info("starting training")
                mbn.reload(flag_use_trained=False)
                trainer.train()
                trainer.bps_for_training.clear()
                logging.info("training succesful")
            except Exception as e:
                with open(log_dir + "/last_input.pickle", "wb") as conn:
                    pickle.dump((datetime.now(), trainer.bps_for_training), conn)
                logging.error(e)
                mbn.__init__(translator=translator, flattener=flattener, tresh_yes=tresh_yes)

                return {"error": str(e)}

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

    # app.run(args.ip, args.port, debug=True)
    http_server = WSGIServer((args.ip, args.port), app, log=None, error_log=None)
    http_server.serve_forever()