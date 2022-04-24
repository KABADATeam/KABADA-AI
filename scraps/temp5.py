import pickle
from pprint import pprint
from re import findall
from BayesNetwork import MultiNetwork
from Translator import Flattener

with open("../bp.pickle", "rb") as conn:
    bp = pickle.load(conn)


flattener = Flattener()
mbn = MultiNetwork()
guids_by_bn = flattener(bp, flag_generate_plus_one=True)

out = mbn.predict_all(guids_by_bn)

pprint(out)

# print(findall('03f70344-c4f5-456a-bbfe-94dde489b31c', str(bp)))
# print(bp['plan'].keys())

# pprint(bp['plan']['channels'][1].keys())
# pprint(bp['plan']['channels'][1])
