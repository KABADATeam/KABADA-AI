from pprint import pprint
from tests.body_generators import PredictBodyGen
from Translator import Flattener, BPMerger
from hashlib import md5

def is_bps_identical(bp1, bp2):
    f1 = flattener(bp1)
    f2 = flattener(bp2)

    if len(f1) != len(f2):
        return False

    f1 = sorted(f1, key=lambda x: x[0])
    f2 = sorted(f2, key=lambda x: x[0])

    for (bpname1, guids1, id_bp1), (bpname2, guids2, id_bp1) in zip(f1, f2):
        if bpname1 != bpname2:
            return False
        if set(guids1) != set(guids2):
            return False
    return True

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
