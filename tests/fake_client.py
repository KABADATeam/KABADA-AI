import json
import requests
from config import repo_dir

class Action:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.__dict__.update(kwargs)

    def __getitem__(self, item):
        return self.args[item]

    def get_json(self):
        return {k: v for k, v in self.__dict__.items() if k != "args"}

    def get_url(self):
        return 'http://localhost:2222/' + action.endpoint

with open(repo_dir + "\\translation\\customer_segments.json", "r") as conn:
    translation = json.load(conn)


actions = [
    Action(endpoint="start_session", id_session=0, bn_name="customer_segments"),
    Action(endpoint="start_session", id_session=1, bn_name="customer_segments"),
    Action(endpoint="give_evidence", id_session=0, bn_name="customer_segments", evidence=translation["Consumer segments"]["Age group"]["Under 12"]),
    Action(endpoint="give_evidence", id_session=1, bn_name="customer_segments", evidence=translation["Consumer segments"]["Age group"]["35 - 64"]),
    Action(endpoint="delete_evidence", id_session=0, bn_name="customer_segments", evidence=translation["Consumer segments"]["Age group"]["Under 12"]),
    Action(endpoint="predict", id_session=1, bn_name="customer_segments", evidence=translation["Consumer segments"]["Age group"]["35 - 64"]),
    Action(endpoint="predict", id_session=1, bn_name="customer_segments", evidence=translation["Consumer segments"]["Age group"]["All age groups"])
]

# print(translation["Consumer segments"]["Age group"]["Under 12"])

for action in actions:
    # print(action.get_json())
    # print(action.get_url())
    r = requests.post(action.get_url(), json=action.get_json(), verify=False)
    print(json.loads(r.text))
    # exit()
