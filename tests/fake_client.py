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
        json_body = {k: v for k, v in self.__dict__.items() if k not in ("args", "name")}
        print(json_body)
        return json_body

    def get_url(self):
        return 'http://localhost:2222/' + action.name

class StartSession(Action):
    def __init__(self, *args, **kwargs):
        Action.__init__(self, *args, **kwargs)
        self.name = "start_session"

class EndSession(Action):
    def __init__(self, *args, **kwargs):
        Action.__init__(self, *args, **kwargs)
        self.name = "end_session"

class GiveEvidence(Action):
    def __init__(self, *args, **kwargs):
        Action.__init__(self, *args, **kwargs)
        self.name = "give_evidence"

class DeleteEvidence(Action):
    def __init__(self, *args, **kwargs):
        Action.__init__(self, *args, **kwargs)
        self.name = "delete_evidence"

class Predict(Action):
    def __init__(self, *args, **kwargs):
        Action.__init__(self, *args, **kwargs)
        self.name = "predict"


with open(repo_dir + "\\translation\\customer_segments.json", "r") as conn:
    translation = json.load(conn)


actions = [
    StartSession(id_session=0, bn_name="customer_segments"),
    StartSession(id_session=1, bn_name="customer_segments"),
    GiveEvidence(id_session=0, bn_name="customer_segments", evidence=translation["Consumer segments"]["Age group"]["Under 12"]),
    GiveEvidence(id_session=1, bn_name="customer_segments", evidence=translation["Consumer segments"]["Age group"]["35 - 64"]),
    EndSession(id_session=1),
    DeleteEvidence(id_session=0, bn_name="customer_segments", evidence=translation["Consumer segments"]["Age group"]["Under 12"]),
    Predict(id_session=1, bn_name="customer_segments", evidence=translation["Consumer segments"]["Age group"]["35 - 64"]),
    Predict(id_session=1, bn_name="customer_segments", evidence=translation["Consumer segments"]["Age group"]["All age groups"])
]

for action in actions:
    # print(action.get_json())
    # print(action.get_url())
    print("----------------------- " + action.name)
    r = requests.post(action.get_url(), json=action.get_json(), verify=False)
    print(json.loads(r.text))
    print("-----------------------")
    # exit()
