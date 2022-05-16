import json
from BayesNetwork import MultiNetwork, check_recomendation_generation, generate_bn_sample
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
from Trainer import check_training

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
    with open(repo_dir + "/docs/Texter.txt", "r", encoding="cp866") as conn:
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
            if {*guid} == {"?"}:
                continue
            try:
                literal_eval(guid)
                continue
            except:
                pass
            val1, kind1 = dict_guid2stuff[guid]
            s = list(stuff.keys())[0]
            val, kind = s.split(":kind")
            if not (val == val1 and int(kind) == kind1):
                raise ValueError(bn_name, val, val1, int(kind), kind1)


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
                    # print(bn_name, val, main_k2v[node])
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
        counter1.update((guid for guid in guids if guid[-1] != "*"))

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


def check_sub_bn_cnts():
    mbn = MultiNetwork()
    node_names = {*mbn.bns['main'].get_node_names()}
    for bn_name in mbn.bns:
        if bn_name not in ("main", "swot"):
            assert "num_" + bn_name in node_names, f"no num node for {bn_name}"
            assert bn_name in mbn.sampling_order, f"{bn_name} not in sampling_order"

    for child, parents in mbn.sub_bn_relations.items():
        i_child = mbn.sampling_order.index(child)
        for parent, relation in parents.items():
            i_parent = mbn.sampling_order.index(parent)
            assert i_child > i_parent


def check_correct_binary_variable_detection():
    from itertools import chain
    mbn = MultiNetwork()
    set_binary_variables = set()
    for node in mbn.bns['main'].get_node_names():
        if "no" in {*mbn.bns['main'].net.get_outcome_ids(node)}:
            set_binary_variables.add(node)
    set_binary_variables_from_translator = set(chain(*(_ for _ in mbn.translator.dict_binary_nodes.values())))
    # print(set_binary_variables_from_translator.difference(set_binary_variables))
    # print(set_binary_variables.difference(set_binary_variables_from_translator))
    # print(len(set_binary_variables_from_translator), len(set_binary_variables))
    assert set_binary_variables == set_binary_variables_from_translator


def check_variable_names_in_translations():
    mbn = MultiNetwork()

    fs_translations = sorted(glob(join(repo_dir, "translation", "*.json")))
    dict_bn2varnames = defaultdict(set)

    for f in fs_translations:
        bn_name = basename(f).replace(".json", "")
        with open(f, "r") as conn:
            translation = json.load(conn)
            for guid, trans in translation.items():
                for _, kw_dicts in trans.items():
                    for kw_dict in kw_dicts:
                        for varname, value in kw_dict.items():
                            dict_bn2varnames[bn_name].add(varname)

    for bn_name, bn in mbn.bns.items():
        if bn_name != "main":
            assert {*bn.get_node_names()} == dict_bn2varnames[bn_name]


def check_translation_variable_name_value_pairs_are_ok():
    mbn = MultiNetwork()

    for bn_name, pairs in mbn.translator.lookup.values():
        for varname, value in pairs:
            assert value in mbn.bns[bn_name].net.get_outcome_ids(varname), (bn_name, varname, value)
            assert value in mbn.bns["main"].net.get_outcome_ids(varname), ("main", varname, value)


def check_predict_endpoint():
    from ai_rest_api import predict
    from tests.body_generators import PredictBodyGen

    B = 1000
    pred_body_gen = PredictBodyGen()
    lens = []
    for _ in range(B):
        bp = pred_body_gen()
        reco = predict(bp)
        lens.append(len(reco['plan']))
    print(Counter(lens))
    # exit()


if __name__ == "__main__":
    check_predict_endpoint()
    check_translation_variable_name_value_pairs_are_ok()
    check_variable_names_in_translations()
    check_correct_binary_variable_detection()
    check_sub_bn_cnts()
    check_bp_flatten_names_to_bns()
    no_translation_same_key()
    check_translations_or_bns_not_missing()
    check_variable_names()
    validate_wrt_texter()
    check_if_all_nets_in_main()
    check_all_translationalble_guids_in_full_bp()
    check_recomendation_generation()
    generate_bn_sample()
    check_training()
    # check_bp_flattener()
    print("everythings OK :)")