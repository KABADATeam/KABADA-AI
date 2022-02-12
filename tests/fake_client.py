import sys
sys.path.insert(0, "/")
import json
import requests
from os.path import join
from config import repo_dir
from tests.body_generators import PredictBodyGen

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

    def generate_bp(self):
        pass


with open(join(repo_dir, "translation", "customer_segments.json"), "r") as conn:
    translation = json.load(conn)

pred_body_gen = PredictBodyGen()
actions = [
    PredictAll(id_session=0, body_json=pred_body_gen())
]

for action in actions:
    print("----------------------- " + action.name)
    r = requests.post(action.get_url(), json=action.get_json(), verify=False)
    print(json.loads(r.text))
    print("-----------------------")
    # exit()
