import json
from glob import glob
from os.path import join, basename
from config import repo_dir
from copy import deepcopy
from pprint import pprint
from re import findall
from ast import literal_eval
import numpy as np
import random
from collections import defaultdict
from Translator import Flattener

# seed = 3
# np.random.seed(seed)
# random.seed(seed)

flattener = Flattener()

class PredictBodyGen:
    def __init__(self, flag_fake_guids=False):
        self.flag_fake_guids = flag_fake_guids
        fs = sorted(glob(join(repo_dir, "translation", "*.json")))
        self.guids = []
        for f in fs:
            # bn_name = basename(f).replace(".json", "")
            with open(f, "r") as conn:
                translation = json.load(conn)
                self.guids.extend(translation.keys())

        if self.flag_fake_guids:
            for i in range(len(self.guids)):
                if np.random.uniform() > 0.5:
                    self.guids[i] = ''.join(random.sample(self.guids[i],len(self.guids[i])))

        with open(join(repo_dir, "docs", "bp_flatten_names_to_bns.json"), "r") as conn:
            self.bp2bn = json.load(conn)
        self.bn2bp = {v: k for k, v in self.bp2bn.items()}

    def impose_one_value_per_bn_variable(self, guids):
        np.random.shuffle(guids)
        set_prefixes = set()
        i = 0
        while i < len(guids):
            # prefix = guids[i]
            split = guids[i].split("::")
            prefix = "::".join(split[:(len(split)-1)])
            if prefix in set_prefixes:
                guids.pop(i)
                continue
            i += 1
            set_prefixes.add(prefix)

    def __call__(self, *args, **kwargs):
        n_sample = int(len(self.guids) * 0.3)
        guids = list(np.random.choice(self.guids, n_sample, replace=False))
        self.impose_one_value_per_bn_variable(guids)
        bp = flattener.back_one_recomendation(guids)
        # guids_by_bn = defaultdict(list)
        # for guid in guids:
        #     for bp_name, bn_name in self.bp2bn.items():
        #         if bp_name in guid:
        #             guids_by_bn
        #
        #     print(self.bp2bn.keys())
        #     print(guid)
        #     exit()
        #
        # print(guids)
        # exit()
        # bp = flattener.back(guids_by_bn)
        bp['location'] = "some_location"
        if 'plan' not in bp:
            bp['plan'] = {}
        bp['plan']['businessPlan_id'] = "some_id"
        return bp


if __name__ == "__main__":
    from Translator import Translator

    translator = Translator()
    generator = PredictBodyGen()

    bp = generator()
    bag_guid = flattener(bp)
    for bp_name, guids, id_bp in bag_guid:
        pprint(translator(guids))
