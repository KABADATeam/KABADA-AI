import pickle
from pprint import pprint

with open("../bp.pickle", "rb") as conn:
    bp = pickle.load(conn)

pprint(bp['plan']['valueProposition'][0].keys())

# pprint(bp['plan']['valueProposition'][0]['productFeatures'])
