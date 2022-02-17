from pprint import pprint
from tests.body_generators import PredictBodyGen
from Translator import Flattener, BPMerger
from hashlib import md5

gen = PredictBodyGen()
flattener = Flattener()


for _ in range(1000):
    bp0 = gen()

    location = bp0["location"]
    id_bp = bp0['plan']['businessPlan_id']

    h_before = md5(str(bp0).encode('utf-8')).hexdigest()
    guids_by_bn = flattener(bp0)

    bp = flattener.back(guids_by_bn)
    bp['location'] = location
    bp['plan']['businessPlan_id'] = id_bp
    h_after = md5(str(bp).encode('utf-8')).hexdigest()

    print(h_before, h_after)
    if h_before != h_after:
        pprint(bp0)
        print("---------------------")
        pprint(bp)
        exit()
