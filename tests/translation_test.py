import json
from BayesNetwork import MultiNetwork
from glob import glob
from os.path import join, basename
from config import repo_dir
from copy import deepcopy
from pprint import pprint
from re import findall
from ast import literal_eval
from collections import defaultdict

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


def check_variable_names():
    net = MultiNetwork()

    fs = sorted(glob(join(repo_dir, "translation", "*.json")))
    for f in fs:
        bn_name = basename(f).replace(".json", "")
        print(bn_name)
        net.add_net(bn_name)

        with open(f, "r") as conn:
            translation = json.load(conn)

        leafs = traverse_leafs(translation)

        varnames_correct = net.bns[bn_name].get_node_names()
        for varname in [list(k.keys())[0] for k in leafs]:
            if varname not in varnames_correct:
                raise ValueError(f"{varname} not a note name for {bn_name}")
        # net.predict(bn_name, leafs)

def parse_texter():
    with open("../docs/Texter.txt", "r", encoding="cp866") as conn:
        codes = conn.read().split("\n")

    dict_guid2stuff = {}
    for code in codes:
        try:
            a = literal_eval(findall(r"(\{.*\})", code)[0])
        except Exception as e:
            print(e)
            continue

        if len(a) == 0:
            continue

        dict_guid2stuff[a["Id"]] = a["Value"], a["Kind"]
    return dict_guid2stuff

def validate_wrt_texter():
    dict_guid2stuff = parse_texter()
    fs = sorted(glob(join(repo_dir, "translation", "*.json")))
    for f in fs:
        bn_name = basename(f).replace(".json", "")
        with open(f, "r") as conn:
            translation = json.load(conn)

        for guid, stuff in translation.items():
            # print(dict_guid2stuff[guid])
            guid = guid.split("::")[-1]
            val1, kind1 = dict_guid2stuff[guid]
            s = list(stuff.keys())[0]
            val, kind = s.split(":kind")
            if not (val == val1 and int(kind) == kind1):
                raise ValueError( val, val1, int(kind), kind1)


def check_bp_flattener():
    from Translator import Flattener
    flattener = Flattener()
    guids = flattener({
            "a": {"a1": ["a11", "a12"], "a2": ["a21", "a22"]},
            "b": {"b1": ["b11"], "b2": ["b21", "b22", {"b23": ["b231"]}]},
        })
    pprint(guids)
    guids = flattener(flattener.full_bp)
    pprint(flattener.back(guids))


def check_if_all_nets_in_main():
    mbn = MultiNetwork()
    main_k2v = defaultdict(set)
    for node in mbn.bns["main"].get_node_names():
        for i in range(mbn.bns["main"].net.get_outcome_count(node)):
            main_k2v[node].add(mbn.bns["main"].net.get_outcome_id(node, i))

    for bn_name in mbn.bns.keys():
        if bn_name != "main":
            for node in mbn.bns[bn_name].get_node_names():
                assert node in main_k2v
                for i in range(mbn.bns[bn_name].net.get_outcome_count(node)):
                    val = mbn.bns[bn_name].net.get_outcome_id(node, i)
                    assert val in main_k2v[node]

if __name__ == "__main__":
    check_variable_names()
    validate_wrt_texter()
    check_if_all_nets_in_main()
    # check_bp_flattener()
    print("everythings OK :)")