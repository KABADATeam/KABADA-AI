import numpy as np
from pprint import pprint
from tests.body_generators import PredictBodyGen
from BayesNetwork import MultiNetwork
from Translator import Translator, Flattener
from collections import defaultdict, Counter
import pandas as pd
from itertools import product, chain
import pysmile
import pickle
from config import path_temp_data_file


def sample_permutations(guids_by_bn, mbn):
    autocompletable = set(chain(*mbn.translator.dict_binary_nodes.values()))

    childkey2parentkey = []
    for bn_name, kvs in mbn.sub_bn_relations.items():
        for parent, relation in kvs.items():
            childkey = mbn.flattener.bn2bp[bn_name] + "::" + relation[1]
            parentkey = mbn.flattener.bn2bp[parent] + "::id"
            childkey2parentkey.append((
                childkey + "::",
                parentkey + "::"
            ))
            break
    set_childkey2parentkey = set(chain(*childkey2parentkey))
    # guids_by_bn = flattener(guids_by_bn)
    # print(guids_by_bn)
    # print(sorted({*mbn.bns.keys()}.difference(set((_[0] for _ in guids_by_bn)))))
    # exit()
    row_common_only_in_bn = {
        "num_" + bn_name: f"num{cnt}" if cnt < 5 else "num_more"
        for bn_name, cnt in Counter((_[0] for _ in guids_by_bn if _[0] != "plan")).items()
    }

    bnname2bns = defaultdict(list)

    max_per_bn_name = 2
    max_perms_generate = 10000
    # pprint(guids_by_bn)

    for bn_name, guids, id_bp in guids_by_bn:
        if len(bnname2bns[bn_name]) < max_per_bn_name:
            bnname2bns[bn_name].append(guids)

    n_perms = np.prod([len(v) for v in bnname2bns.values()])

    data_entries = []
    for iperm, guids in enumerate(product(*bnname2bns.values())):
        if iperm == max_perms_generate:
            break
        guids = list(chain(*guids))
        flag_subbn_associations_are_correct = True
        for childkey, parentkey in childkey2parentkey:
            child = None
            parent = None
            for guid in guids:
                if childkey in guid:
                    child = guid.replace(childkey, "")
                if parentkey in guid:
                    parent = guid.replace(parentkey, "")
                if parent is not None and child is not None:
                    break

            # xor
            # pprint(guids)
            # print(childkey, parentkey)
            # print(parent, child)
            assert (parent is not None and child is not None) or (parent is None and child is None)
            flag_subbn_associations_are_correct = parent == child
            if not flag_subbn_associations_are_correct:
                break

        if flag_subbn_associations_are_correct:

            # not adding child/parent associations
            clean_guids = []
            for guid in guids:
                flag_add = True
                for k in set_childkey2parentkey:
                    if k in guid:
                        flag_add = False
                        break
                if flag_add:
                    clean_guids.append(guid)

            row = {}
            for bn_name, pairs in translator(clean_guids).items():
                for varname, value in pairs:
                    row[varname] = value
            row.update(row_common_only_in_bn)

            for varname in autocompletable.difference(row.keys()):
                row[varname] = 'no'
            data_entries.append(row)

    return data_entries


class Trainer:
    def __init__(self, mbn=None):
        if mbn is None:
            self.mbn = MultiNetwork()
        self.flattener = Flattener()
        self.translator = Translator()
        self.bps_for_training = []

    def add_bp(self, bp):
        self.bps_for_training.append(bp)

    def train(self):

        data_entries = []
        for bp in self.bps_for_training:
            subdata_entries = sample_permutations(bp, self.mbn)
            data_entries.extend(subdata_entries)
        bn_datas = {"main": pd.DataFrame(data_entries)}

        self.mbn.learn_all(bn_datas)


if __name__ == "__main__":
    np.random.seed(3)

    flattener = Flattener()
    translator = Translator()
    mbn = MultiNetwork(tresh_yes=0.0)

    trainer = Trainer()
    for _ in range(2):
        guids_by_bn = mbn.sample_all()
        trainer.add_bp(guids_by_bn)
    trainer.train()