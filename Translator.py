import json
from glob import glob
from os.path import join, basename
from config import repo_dir
from pprint import pprint
from collections import defaultdict


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
    translator = Translator()
