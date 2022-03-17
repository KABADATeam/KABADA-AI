from Translator import Flattener, Translator, BPMerger, copy_attribute
import json
from config import repo_dir
from pprint import pprint
from BayesNetwork import MultiNetwork
from os.path import join
import hashlib
flattener = Flattener()
net = MultiNetwork()




with open(repo_dir + "/test_bps/id_example.json", "r") as conn:
    bp = json.load(conn)

# pprint(bp)
# exit()

# pprint(bp)
# exit()
guids_by_bn = flattener(bp)
# pprint(guids_by_bn)
recomendations_by_bn = net.predict_all(guids_by_bn)
# pprint(recomendations_by_bn)
# exit()

bp_new = flattener.back(recomendations_by_bn)

copy_attribute(bp, bp_new)
pprint(bp_new)