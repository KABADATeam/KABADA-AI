import sys
sys.path.insert(0, ".")
import json
import requests
from os.path import join
from config import repo_dir, path_ip_port_json
from glob import glob
import os
from tests.body_generators import PredictBodyGen

ip = 'localhost'
port = '2222'

if os.path.exists(path_ip_port_json):
    with open(path_ip_port_json, "r") as conn:
        ip_port = json.load(conn)
        if "ip" in ip_port:
            ip = ip_port['ip']
        if "port" in ip_port:
            port = ip_port['port']

class Action:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.__dict__.update(kwargs)

    def __getitem__(self, item):
        return self.args[item]

    def get_json(self):
        json_body = {k: v for k, v in self.__dict__.items() if k not in ("args", "name")}
        print(json_body)
        return json_body

    def get_url(self):
        return f'http://{ip}:{port}/' + action.name


class PredictAll(Action):
    def __init__(self, *args, **kwargs):
        Action.__init__(self, *args, **kwargs)
        self.name = "predict"

translation = {}
for f in glob(join(repo_dir, "translation", "*.json")):
    with open(f, "r") as conn:
        translation.update(json.load(conn))

pred_body_gen = PredictBodyGen()
# actions = [
#     PredictAll(**pred_body_gen()),
#     PredictAll(**pred_body_gen()),
#     PredictAll(**pred_body_gen()),
#     PredictAll(**pred_body_gen())
# ]

actions = []
for _ in range(1000):
    actions.append(PredictAll(**pred_body_gen()))

for action in actions:
    print("----------------------- " + action.name)
    r = requests.post(action.get_url(), json=action.get_json(), verify=False)
    # print(json.loads(r.text))
    print(r.text)
    print("-----------------------")
    # exit()
