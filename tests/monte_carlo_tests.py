import pandas as pd
import numpy as np
from pprint import pprint
from BayesNetwork import MultiNetwork
from Translator import Translator
from collections import defaultdict, Counter
from scipy.stats import chisquare


def check_main_together_with_translations():
    tab = pd.read_csv("../bayesgraphs/main.txt", sep=" ")

    translator = Translator()
    mbn = MultiNetwork(tresh_yes=0.0)

    for c in tab.columns:
        other_columns = list(tab.columns)
        other_columns.remove(c)
        sampled = []
        for i, row in tab.iterrows():
            bp = defaultdict(set)
            for k, v in row.items():
                if k != c:
                    if k == 'nace' or "num_" in k:
                        bn_name0 = "plan"
                        continue
                    bn_name0 = None
                    for bn_name in mbn.bns.keys():
                        if bn_name != "main":
                            if k in mbn.bns[bn_name].get_node_names():
                                bn_name0 = bn_name
                    assert bn_name0 is not None, f"no bn for {k}"
                    bp[bn_name0].add((k, v))

            bp = [(k, v, None) for k, v in bp.items()]

            translations_by_bn = translator.back(bp, flag_dont_check_bn_name=True)

            recos = mbn.predict_all(translations_by_bn, flag_noisy=True,
                                    flag_translate_output=False, flag_with_nos=True)
            value0 = None
            for _, pairs, _ in recos:
                for varname, value in pairs:
                    if varname == c:
                        value0 = value
                        break
                if value0 is not None:
                    break
            assert value0 is not None
            sampled.append(value0)

        f_obs = Counter(sampled)
        f_exp = Counter(tab[c])

        print(f_obs, f_exp)

        ks = sorted(f_obs.keys() | f_exp.keys())
        f_obs = np.array([f_obs.get(k, 0) for k in ks])
        f_exp = np.array([f_exp.get(k, 0) for k in ks])
        # f_obs = f_obs / np.sum(f_obs)
        # f_exp = f_exp / np.sum(f_exp)
        print(chisquare(f_obs, f_exp=f_exp, ddof=0, axis=0).pvalue)

        exit()


def check_seperate_bn_simulation():
    translator = Translator()
    mbn = MultiNetwork()
    for bn_name, bn in mbn.bns.items():
        pvals = {}
        if bn_name != "main":
            tab = pd.read_csv(f"../bayesgraphs/{bn_name}.txt", sep=" ")
            bn.tresh_yes = 0.0
            for c in tab.columns:
                other_columns = list(tab.columns)
                other_columns.remove(c)
                sampled = []
                for i, row in tab.iterrows():
                    list_evidence = []
                    for k, v in row.items():
                        if k != c:
                            list_evidence.append((k, v))
                    recos = bn.predict_popup(list_evidence, flag_with_nos=True, flag_noisy=True, targets=[c])
                    for varname, value in recos:
                        if varname == c:
                            sampled.append(value)

                f_obs = Counter(sampled)
                f_exp = Counter(tab[c])

                ks = sorted(f_obs.keys() | f_exp.keys())
                f_obs = np.array([f_obs.get(k, 0) for k in ks])
                f_exp = np.array([f_exp.get(k, 0) for k in ks])
                # f_obs = f_obs / np.sum(f_obs)
                # f_exp = f_exp / np.sum(f_exp)
                pvals[c] = chisquare(f_obs, f_exp=f_exp, ddof=0, axis=0).pvalue
                assert pvals[c] > 0.05

# check_seperate_bn_simulation()
check_main_together_with_translations()