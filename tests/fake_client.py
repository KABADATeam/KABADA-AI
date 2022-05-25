import sys
sys.path.insert(0, ".")
import json
import requests
from os.path import join
from config import repo_dir, path_ip_port_json
from glob import glob
import os
from pprint import pprint
from tests.body_generators import PredictBodyGen

ip = 'localhost'
port = 2222

if os.path.exists(path_ip_port_json):
    with open(path_ip_port_json, "r") as conn:
        ip_port = json.load(conn)
        if "ip" in ip_port:
            ip = ip_port['ip']
        if "port" in ip_port:
            port = int(ip_port['port'])


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


class LearnAll(Action):
    def __init__(self, *args, **kwargs):
        Action.__init__(self, *args, **kwargs)
        self.name = "learn"
        self.isFirst = False
        self.isLast = False


mode_predict_testing = 0
mode_train_testing = 1

mode = mode_predict_testing
# mode = mode_train_testing

pred_body_gen = PredictBodyGen()
flag_gen_from_bn = False
actions = []
for _ in range(100 if mode == mode_predict_testing else 100):
    if mode == mode_predict_testing:
        if flag_gen_from_bn:
            actions.append(PredictAll(**pred_body_gen.generate_from_bn(flag_bp_structure=True)))
        else:
            actions.append(PredictAll(**pred_body_gen()))
    elif mode == mode_train_testing:
        if flag_gen_from_bn:
            actions.append(LearnAll(**pred_body_gen.generate_from_bn(flag_bp_structure=True)))
        else:
            actions.append(LearnAll(**pred_body_gen()))
    else:
        raise ValueError

if mode == mode_train_testing:
    # with open("AI_learning.json", "r") as conn:
    #     actions[0] = json.load(conn)
    actions[0].isFirst = True
    actions[-1].isLast = True

for action in actions:
    print("----------------------- " + action.name)
    # pprint(action.get_json())
    # exit()
    r = requests.post(action.get_url(), json=action.get_json(), verify=False)
    # print(json.loads(r.text))
    print(r.text)
    print("-----------------------")
    # exit()
