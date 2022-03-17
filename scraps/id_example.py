from Translator import Flattener, Translator, BPMerger, copy_attribute, is_bps_identical
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

def check_with_recomendations():
    guids_by_bn = flattener(bp)
    # pprint(guids_by_bn)
    recomendations_by_bn = net.predict_all(guids_by_bn)
    # pprint(recomendations_by_bn)
    # exit()

    bp_new = flattener.back(recomendations_by_bn)

    # copy_attribute(bp, bp_new)

    pprint(bp)
    print(11111111111111)
    pprint(bp_new)


def check_only_transformation():
    guids_by_bn = flattener(bp)

    bp_new = flattener.back(guids_by_bn)

    pprint(bp)
    print(11111111111111)
    pprint(bp_new)
    print(is_bps_identical(bp, bp_new))


check_with_recomendations()
check_only_transformation()