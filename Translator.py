import json
from glob import glob
from os.path import join, basename
from config import repo_dir
from pprint import pprint
from collections import defaultdict

class Translator:
    def __init__(self):
        fs = sorted(glob(join(repo_dir, "translation", "*.json")))

        self.lookup = {}
        for f in fs:
            bn_name = basename(f).replace(".json", "")
            with open(f, "r") as conn:
                translation = json.load(conn)

            for guid, trans in translation.items():
                self.lookup[guid] = (bn_name, list(trans.values())[0])

    def __call__(self, bag_guids, *args, **kwargs):
        translation = defaultdict(list)
        for guid in bag_guids:
            bn_name, list_evidence = self.lookup[guid]
            translation[bn_name].extend(list_evidence)
        return translation

    def back(self, bp):
        # TODO how to handle cases like "All age groups" ?
        for bn_name, list_evidence in bp.items():
            pass

        return {}


if __name__ == "__main__":
    translator = Translator()