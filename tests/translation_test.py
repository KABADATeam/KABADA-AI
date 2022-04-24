import json
from BayesNetwork import MultiNetwork
from glob import glob
from os.path import join, basename
from config import repo_dir
from copy import deepcopy
from pprint import pprint
from re import findall
from ast import literal_eval
from collections import defaultdict, Counter
import os
from Translator import Flattener

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


def check_translations_or_bns_not_missing():
    fs_trans = {os.path.basename(f).replace(".json", "") for f in glob(join(repo_dir, "translation", "*.json"))}
    fs_bns = {os.path.basename(f).replace(".xdsl", "") for f in glob(join(repo_dir, "bayesgraphs", "*.xdsl"))}
    # print(fs_bns.difference(fs_trans))
    # print(fs_trans.difference(fs_bns))
    assert fs_trans.issubset(fs_bns)

def no_translation_same_key():
    fs = sorted(glob(join(repo_dir, "translation", "*.json")))
    counter = Counter()
    for f in fs:
        with open(f, "r") as conn:
            translation = json.load(conn)
        counter.update(translation.keys())
    assert counter.most_common()[0][1] == 1

def check_all_translationalble_guids_in_full_bp():
    flattener = Flattener()
    guids_by_bn = flattener(flattener.full_bp)
    counter1 = Counter()
    for bn_name, guids, id_bp in guids_by_bn:
        counter1.update(guids)

    assert counter1.most_common()[0][1] == 1

    fs = sorted(glob(join(repo_dir, "translation", "*.json")))
    counter2 = Counter()
    for f in fs:
        with open(f, "r") as conn:
            translation = json.load(conn)
        counter2.update(translation.keys())
    assert counter2.most_common()[0][1] == 1

    # print(sorted(set(counter1.keys()).difference(counter2.keys())))
    # print(sorted(set(counter2.keys()).difference(counter1.keys())))
    # exit()
    assert counter1.keys() == counter2.keys()

def check_bp_flatten_names_to_bns():
    flattener = Flattener()
    mbn = MultiNetwork()
    guids_by_bn = flattener(flattener.full_bp)
    bn_names = {_[0] for _ in guids_by_bn}
    for bn_name in bn_names:
        if bn_name in mbn.bns:
            assert bn_name in flattener.bn2bp


if __name__ == "__main__":
    check_bp_flatten_names_to_bns()
    no_translation_same_key()
    check_translations_or_bns_not_missing()
    check_all_translationalble_guids_in_full_bp()
    check_variable_names()
    validate_wrt_texter()
    check_if_all_nets_in_main()
    # check_bp_flattener()
    print("everythings OK :)")