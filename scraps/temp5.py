import pickle
from pprint import pprint
from re import findall

with open("../bp.pickle", "rb") as conn:
    bp = pickle.load(conn)

# print(findall('03f70344-c4f5-456a-bbfe-94dde489b31c', str(bp)))


print(bp['plan'].keys())

# pprint(bp['plan']['channels'][1].keys())
# pprint(bp['plan']['channels'][1])
