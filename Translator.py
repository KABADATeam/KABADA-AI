import json
from glob import glob
from os.path import join, basename
from config import repo_dir
from pprint import pprint
from collections import defaultdict
from copy import deepcopy


def rec_accumulate_guids(bp, path, guids):
    if isinstance(bp, str) or isinstance(bp, int) or isinstance(bp, float):
        guids.append(path + [str(bp)])

    if isinstance(bp, dict):
        for k, v in bp.items():
            rec_accumulate_guids(v, path + [k], guids)

    if isinstance(bp, list):
        for v in bp:
            rec_accumulate_guids(v, path, guids)


def rec_change_bp(bp, path, sep="::"):
    if isinstance(bp, dict):
        for k in list(bp.keys()):
            v = bp[k]
            if isinstance(v, str) or isinstance(bp, int) or isinstance(bp, float):
                bp[k] = sep.join(path + [str(v)])
            else:
                rec_change_bp(v, path + [k], sep=sep)

    if isinstance(bp, list):
        for i in range(len(bp)):
            if isinstance(bp[i], str) or isinstance(bp[i], int) or isinstance(bp[i], float):
                bp[i] = sep.join(path + [str(bp[i])])
            else:
                rec_change_bp(bp[i], path, sep=sep)


def rec_delete_missing(bp, path, set_guids, sep="::"):
    if isinstance(bp, dict):
        for k in list(bp.keys()):
            v = bp[k]
            if isinstance(v, str) or isinstance(bp, int) or isinstance(bp, float):
                if sep.join(path + [str(v)]) not in set_guids:
                    del bp[k]
            else:
                rec_delete_missing(v, path + [k], set_guids, sep=sep)

    if isinstance(bp, list):
        inds_drop = []
        for i in range(len(bp)):
            if isinstance(bp[i], str) or isinstance(bp[i], int) or isinstance(bp[i], float):
                if sep.join(path + [str(bp[i])]) not in set_guids:
                    inds_drop.append(i)
            else:
                rec_delete_missing(bp[i], path, set_guids, sep=sep)

        for i in reversed(sorted(inds_drop)):
            bp.pop(i)


class Flattener:
    def __init__(self, sep="::"):
        self.sep = sep
        with open(join(repo_dir, "docs", "full_bp.json"), "r") as conn:
            self.full_bp = json.load(conn)
        # self.full_guid_bp = deepcopy(self.full_bp)
        # rec_change_bp(self.full_guid_bp, [], sep=sep)

    def __call__(self, bp):
        guids = []
        rec_accumulate_guids(bp, [], guids)
        for i in range(len(guids)):
            guids[i] = "::".join(guids[i])
        return guids

    def back(self, guids):
        set_guids = set(guids)
        bp = deepcopy(self.full_bp)
        rec_delete_missing(bp, [], set_guids, sep=self.sep)
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
        guids = []
        for guid, (bn_name, values) in self.lookup.items():
            necessary_condition = {tuple(a.items())[0] for a in values}
            if necessary_condition.issubset(bp[bn_name]):
                guids.append(guid)

        return guids


if __name__ == "__main__":
    flattener = Flattener()
    print(flattener({
        "a": {"a1": ["a11", "a12"], "a2": ["a21", "a22"]},
        "b": {"b1": ["b11"], "b2": ["b21", "b22", "b23"]},
    }))
    translator = Translator()
