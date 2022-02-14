import sys
sys.path.insert(0, "/")
import json
import requests
from os.path import join
from config import repo_dir
from tests.body_generators import PredictBodyGen
from flask import jsonify


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
        return 'http://localhost:2222/' + action.name


class PredictAll(Action):
    def __init__(self, *args, **kwargs):
        Action.__init__(self, *args, **kwargs)
        self.name = "predict"


with open(join(repo_dir, "translation", "customer_segments.json"), "r") as conn:
    translation = json.load(conn)

pred_body_gen = PredictBodyGen()
actions = [
    PredictAll(**pred_body_gen()),
    PredictAll(**pred_body_gen()),
    PredictAll(**pred_body_gen()),
    PredictAll(**pred_body_gen())
]

# import json
# a = json.loads(str(actions[0].get_json()).replace("'", '"'))
# print(a)
# exit()

for action in actions:
    print("----------------------- " + action.name)
    r = requests.post(action.get_url(), json=action.get_json(), verify=False)
    print(r.text)
    print("-----------------------")
    # exit()
