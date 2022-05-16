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
from BayesNetwork import MultiNetwork
from uuid import uuid4

# seed = 3
# np.random.seed(seed)
# random.seed(seed)

flattener = Flattener()

class PredictBodyGen:
    def __init__(self, flag_fake_guids=False):
        self.flag_fake_guids = flag_fake_guids
        self.mbn = None
        fs = sorted(glob(join(repo_dir, "translation", "*.json")))
        self.guids = []
        for f in fs:
            # bn_name = basename(f).replace(".json", "")
            with open(f, "r") as conn:
                translation = json.load(conn)
                self.guids.append(list(translation.keys()))

        if self.flag_fake_guids:
            for j, guids in enumerate(self.guids):
                for i in range(len(guids)):
                    if np.random.uniform() > 0.5:
                        self.guids[j][i] = ''.join(random.sample(self.guids[i],len(self.guids[i])))

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

    def generate_from_bn(self, flag_bp_structure=False):
        if self.mbn is None:
            self.mbn = MultiNetwork()

        guids_by_bn = self.mbn.sample_all()
        if flag_bp_structure:
            return self.mbn.flattener.back(guids_by_bn)
        return guids_by_bn

    def __call__(self, *args, **kwargs):

        guids = []
        for gs in self.guids:
            n_sample = int(np.clip(int(len(gs) * 0.3), 1, np.inf))
            guids.extend(list(np.random.choice(gs, n_sample, replace=False)))
        self.impose_one_value_per_bn_variable(guids)
        bp = flattener.back_one_recomendation(guids)
        guids_by_bn = flattener(bp)

        i0 = np.random.choice(len(guids_by_bn), size=(1,))[0]
        if guids_by_bn[i0][0] == "plan":
            location = "plan::swot"
        else:
            uuid = str(uuid4())
            guids_by_bn[i0] = guids_by_bn[i0][0], guids_by_bn[i0][1], uuid
            location = f"{flattener.bn2bp[guids_by_bn[i0][0]]}::{uuid}"

        bp = flattener.back(guids_by_bn)
        bp['location'] = location
        if 'plan' not in bp:
            bp['plan'] = {}
        bp['plan']['businessPlan_id'] = str(uuid4())
        return bp


if __name__ == "__main__":
    from Translator import Translator

    translator = Translator()
    generator = PredictBodyGen()

    bp = generator()
    bag_guid = flattener(bp)
    for bp_name, guids, id_bp in bag_guid:
        pprint(translator(guids))
