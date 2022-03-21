from Translator import Flattener, Translator, BPMerger
import json
from config import repo_dir
from pprint import pprint
from BayesNetwork import MultiNetwork
from os.path import join
import hashlib
flattener = Flattener()
net = MultiNetwork()

with open(repo_dir + "/test_bps/test_bp.json", "r") as conn:
    bp = json.load(conn)
# with open(repo_dir + "/docs/full_bp.json", "r") as conn:
#     bp = json.load(conn)

# pprint(bp)
guids_by_bn = flattener(bp, flag_generate_plus_one=True)
recomendations_by_bn = net.predict_all(guids_by_bn)
# pprint(recomendations_by_bn)


bp = flattener.back(recomendations_by_bn)
pprint(bp)
