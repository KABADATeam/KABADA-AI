from Translator import Flattener, Translator
import json
from config import repo_dir
from pprint import pprint
from BayesNetwork import MultiNetwork
from os.path import join
import hashlib
flattener = Flattener()
net = MultiNetwork()

with open(repo_dir + "/docs/test_bp.json", "r") as conn:
    bp = json.load(conn)
# with open(repo_dir + "/docs/full_bp.json", "r") as conn:
#     bp = json.load(conn)

# pprint(bp)
guids_by_bn = flattener(bp)
recomendations_by_bn = net.predict_all(guids_by_bn)
# pprint(recomendations_by_bn)
bps = []
for bn_name, recomendations in recomendations_by_bn:
    bp = flattener.back(recomendations)
    bps.append(bp)
    # pprint(bp)
    # exit()
# pprint(bps)
merger = BPMerger()
pprint(merger(bps[0], bps[1]))