import json
from glob import glob
from os.path import join, basename
from config import repo_dir
from pprint import pprint
from collections import defaultdict
from copy import deepcopy
from hashlib import md5


def rec_merge(bp1, bp2, path, bp2bn, sep="::", set_hashes_of_epmty=None):

    if isinstance(bp1, dict):
        assert bp1.keys() == bp2.keys()
        res = {}
        for k in bp1.keys():
            path1 = k if len(path) == 0 else path + sep + k
            res[k] = rec_merge(bp1[k], bp2[k], path1, bp2bn, sep=sep, set_hashes_of_epmty=set_hashes_of_epmty)
        return res

    if isinstance(bp1, list):
        res = bp1 + bp2
        hs = []
        for r in res:
            hs.append(md5(str(r).encode("utf-8")).hexdigest())
            # print(22222, path in bp2bn, r, hs[-1])
        set_unique = set()
        inds_drop = []
        num_unique_hs = len(set(hs))
        for i, h in enumerate(hs):
            if h in set_unique or (h in set_hashes_of_epmty and path in bp2bn and num_unique_hs > 1):
                inds_drop.append(i)
            else:
                set_unique.add(h)
        # TODO merge further, for now it seems unnecessary
        for i in reversed(sorted(inds_drop)):
            res.pop(i)
        return res


class BPMerger:
    def __init__(self, set_hashes_of_epmty):
        with open(join(repo_dir, "docs", "bp_flatten_names_to_bns.json"), "r") as conn:
            self.bp2bn = json.load(conn)
        self.set_hashes_of_epmty = set_hashes_of_epmty

    def __call__(self, bp1, bp2):
        assert bp1.keys() == bp2.keys()
        return rec_merge(bp1, bp2, "", self.bp2bn, sep="::", set_hashes_of_epmty=self.set_hashes_of_epmty)


def rec_accumulate_guids(bp, path, guids, bp2bn, sep="::"):
    if isinstance(bp, str) or isinstance(bp, int) or isinstance(bp, float):
        guids.append(path + sep + str(bp))

    if isinstance(bp, dict):
        for k, v in bp.items():
            if len(path) > 0:
                rec_accumulate_guids(v, path + sep + k, guids, bp2bn, sep=sep)
            else:
                rec_accumulate_guids(v, k, guids, bp2bn, sep=sep)

    if isinstance(bp, list):
        for v in bp:
            if path in bp2bn:
                subguids = []
                rec_accumulate_guids(v, path, subguids, bp2bn, sep=sep)
                if len(subguids) > 0:
                    guids.append((bp2bn[path], subguids))
            else:
                rec_accumulate_guids(v, path, guids, bp2bn, sep=sep)


def rec_delete_missing(bp, path, set_guids, sep="::", set_hashes_of_epmty=None):

    if isinstance(bp, dict):

        for k in list(bp.keys()):
            v = bp[k]
            if isinstance(v, str) or isinstance(bp, int) or isinstance(bp, float):
                if sep.join(path + [str(v)]) not in set_guids:
                    del bp[k]
            else:
                rec_delete_missing(v, path + [k], set_guids, sep=sep,set_hashes_of_epmty=set_hashes_of_epmty)
        if set_hashes_of_epmty is not None:
            # print(1111111111, bp, md5(str(bp).encode("utf-8")).hexdigest())
            set_hashes_of_epmty.add(md5(str(bp).encode("utf-8")).hexdigest())

    if isinstance(bp, list):
        inds_drop = []
        for i in range(len(bp)):
            if isinstance(bp[i], str) or isinstance(bp[i], int) or isinstance(bp[i], float):
                if sep.join(path + [str(bp[i])]) not in set_guids:
                    inds_drop.append(i)
            else:
                rec_delete_missing(bp[i], path, set_guids, sep=sep,set_hashes_of_epmty=set_hashes_of_epmty)

        for i in reversed(sorted(inds_drop)):
            bp.pop(i)
        if set_hashes_of_epmty is not None:
            set_hashes_of_epmty.add(md5(str(bp).encode("utf-8")).hexdigest())


class Flattener:
    def __init__(self, sep="::"):
        self.sep = sep
        with open(join(repo_dir, "docs", "full_bp.json"), "r") as conn:
            self.full_bp = json.load(conn)

        set_hashes_of_epmty = set()
        bp = deepcopy(self.full_bp)
        rec_delete_missing(bp, [], {}, sep=self.sep, set_hashes_of_epmty=set_hashes_of_epmty)

        self.merger = BPMerger(set_hashes_of_epmty=set_hashes_of_epmty)

        with open(join(repo_dir, "docs", "bp_flatten_names_to_bns.json"), "r") as conn:
            self.bp2bn = json.load(conn)

    def __call__(self, bp):
        guids = []
        rec_accumulate_guids(bp, "", guids, self.bp2bn)
        output = []
        default = []
        for guid in guids:
            if isinstance(guid, tuple):
                output.append(guid)
            else:
                default.append(guid)
        output.append(("plan", default))
        return output

    def back_one_recomendation(self, guids):
        set_guids = set(guids)
        bp = deepcopy(self.full_bp)
        rec_delete_missing(bp, [], set_guids, sep=self.sep)
        return bp

    def back(self, recomendations_by_bn):
        bp = None
        for bn_name, recomendations in recomendations_by_bn:
            if bp is None:
                bp = self.back_one_recomendation(recomendations)
            else:
                bp = self.merger(bp, self.back_one_recomendation(recomendations))
        return bp

class Translator:
    def __init__(self):
        fs = sorted(glob(join(repo_dir, "translation", "*.json")))

        self.lookup_uiname = {}
        self.lookup = {}
        for f in fs:
            bn_name = basename(f).replace(".json", "")
            with open(f, "r") as conn:
                translation = json.load(conn)

            for guid, trans in translation.items():
                self.lookup[guid] = (bn_name, list(trans.values())[0])
                self.lookup_uiname[guid] = list(trans.keys())[0]

        self.inverse_lookup = defaultdict(lambda :defaultdict(list))
        for guid, (bn_name, values) in self.lookup.items():
            for varname, value in (tuple(a.items())[0] for a in values):
                self.inverse_lookup[bn_name][varname].append(value)

    def __call__(self, bag_guids, *args, **kwargs):
        translation = defaultdict(list)
        for guid in bag_guids:
            if guid in self.lookup:
                bn_name, list_evidence = self.lookup[guid]
                translation[bn_name].extend(list_evidence)
        return translation

    def back(self, bp):
        guids_by_bn = []
        for bn_name0, values0 in bp:
            guids = []
            for guid, (bn_name, values) in self.lookup.items():
                if bn_name == bn_name0:
                    necessary_condition = {tuple(a.items())[0] for a in values}
                    if necessary_condition.issubset(values0):
                        guids.append(guid)
            guids_by_bn.append((bn_name0, guids))

        return guids_by_bn


if __name__ == "__main__":
    flattener = Flattener()
    print(flattener({
        "a": {"a1": ["a11", "a12"], "a2": ["a21", "a22"]},
        "b": {"b1": ["b11"], "b2": ["b21", "b22", "b23"]},
    }))
    translator = Translator()
