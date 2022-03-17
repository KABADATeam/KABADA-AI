from pprint import pprint
from tests.body_generators import PredictBodyGen
from Translator import Flattener, BPMerger, is_bps_identical
from hashlib import md5


gen = PredictBodyGen()
flattener = Flattener()


for _ in range(1000):
    bp0 = gen()

    location = bp0["location"]
    id_bp = bp0['plan']['businessPlan_id']

    s0 = str(bp0)
    h_before = md5(s0.encode('utf-8')).hexdigest()
    guids_by_bn = flattener(bp0)

    bp = flattener.back(guids_by_bn)
    bp['location'] = location
    bp['plan']['businessPlan_id'] = id_bp
    s = str(bp)
    h_after = md5(s.encode('utf-8')).hexdigest()

    print(h_before, h_after)
    if not is_bps_identical(bp, bp0):
        pprint(bp0)
        print("---------------------")
        pprint(bp)
        # print(s == s0)
        # for i in range(min(len(s), len(s0))):
        #     if s[i] != s0[i]:
        #         print(s[i], s0[i])
        # print(111111111111, len(s), len(s0))
        exit()
