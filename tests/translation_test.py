import json
from BayesNetwork import MultiNetwork
from glob import glob
from os.path import join, basename
from config import repo_dir
from copy import deepcopy

def traverse_leafs(translation):
    translation_flat = deepcopy(translation)
    keys = list(translation_flat.keys())
    leafs = []
    while len(keys) > 0:
        key = keys.pop(0)
        if isinstance(translation_flat[key], list):
            leafs.extend(translation_flat[key])
        else:
            keys.extend(translation_flat[key].keys())
            translation_flat.update(translation_flat[key])

    return leafs

net = MultiNetwork()

fs = sorted(glob(join(repo_dir, "translation", "*.json")))
for f in fs:
    bn_name = basename(f).replace(".json", "")
    net.add_net(bn_name)

    with open(f, "r") as conn:
        translation = json.load(conn)

    leafs = traverse_leafs(translation)

    varnames_correct = net.bns[bn_name].get_node_names()
    for varname in [list(k.keys())[0] for k in leafs]:
        if varname not in varnames_correct:
            raise ValueError(f"{varname} not a note name for {bn_name}")
    # net.predict(bn_name, leafs)
