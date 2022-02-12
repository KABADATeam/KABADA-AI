import json
from glob import glob
from os.path import join, basename
from config import repo_dir
from copy import deepcopy
from pprint import pprint
from re import findall
from ast import literal_eval
import numpy as np
import random

class PredictBodyGen:
    def __init__(self, flag_fake_guids=False):
        self.flag_fake_guids = flag_fake_guids
        fs = sorted(glob(join(repo_dir, "translation", "*.json")))
        self.guids = []
        for f in fs:
            # bn_name = basename(f).replace(".json", "")
            with open(f, "r") as conn:
                translation = json.load(conn)
                self.guids.extend(translation.keys())

        if self.flag_fake_guids:
            for i in range(len(self.guids)):
                if np.random.uniform() > 0.5:
                    self.guids[i] = ''.join(random.sample(self.guids[i],len(self.guids[i])))

    def __call__(self, *args, **kwargs):
        n_sample = int(len(self.guids) * 0.5)
        return list(np.random.choice(self.guids, n_sample))


if __name__ == "__main__":
    from Translator import Translator

    translator = Translator()
    generator = PredictBodyGen()

    bag_guid = generator()

    pprint(translator(bag_guid))
