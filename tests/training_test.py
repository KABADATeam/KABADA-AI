import numpy as np
from pprint import pprint
from tests.body_generators import PredictBodyGen
from BayesNetwork import MultiNetwork
from Translator import Translator, Flattener
from collections import defaultdict, Counter
import pandas as pd
import pysmile
import pickle
from config import path_temp_data_file
np.random.seed(3)

pred_body_gen = PredictBodyGen()
bps_for_training = []
for _ in range(10000):
    np.random.seed(_)
    bps_for_training.append(pred_body_gen.generate_from_bn())

with open("../bp.pickle", "rb") as conn:
    bp = pickle.load(conn)
bps_for_training.append(bp)


translator = Translator()
flattener = Flattener()
mbn = MultiNetwork()


class EmptyFiller:
    def __init__(self):
        self.set_binary_values = {"yes", "no"}
        self.unique_values = defaultdict(set)

    def at_end(self, data):
        for varname, list_vals in data.items():
            s = {*(_ for _ in list_vals if _ is not None)}
            if s.issubset(self.set_binary_values):
                data[varname] = ["no" if entry is None else entry for entry in list_vals]

    def __call__(self, data):
        nmax = -np.inf
        for varname, list_vals in data.items():
            if len(list_vals) > 0:
                self.unique_values[varname].add(list_vals[-1])
            nmax = max(nmax, len(list_vals))

        for varname in data.keys():
            if len(data[varname]) < nmax:
                data[varname].extend([None] * (nmax - len(data[varname])))


empty_filler = EmptyFiller()
bn_datas = defaultdict(lambda: defaultdict(list))
set_seen_variables_in_one_bp = set()
for bp in bps_for_training:
    guids_by_bn = flattener(bp)
    for bn_name, list_guids, id_bp in guids_by_bn:
        for _, pairs in translator(list_guids).items():
            for varname, value in pairs:
                if varname in set_seen_variables_in_one_bp:
                    raise ValueError(varname, set_seen_variables_in_one_bp, guids_by_bn)

                set_seen_variables_in_one_bp.add(varname)
                bn_datas[bn_name][varname].append(value)

        set_seen_variables_in_one_bp.clear()
        empty_filler(bn_datas[bn_name])

for bn_name, bn_data in bn_datas.items():
    empty_filler.at_end(bn_data)
    bn_datas[bn_name] = pd.DataFrame(bn_data)

# print(bn_datas.shape, Counter(bn_datas['geo_location_foreign']))
# for bn_name, bn_data in bn_datas.items():
#     for c in bn_data.columns:
#         print(c, Counter(bn_data[c]))

mbn.learn_all(bn_datas)

