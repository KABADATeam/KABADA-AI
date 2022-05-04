import pandas as pd
import numpy as np
from pprint import pprint
from BayesNetwork import MultiNetwork
from Translator import Translator
from collections import defaultdict, Counter
from scipy.stats import chisquare
import pickle
from sklearn.metrics import f1_score, confusion_matrix, accuracy_score

def check_main_together_with_translations():
    tab = pd.read_csv("../bayesgraphs/main.txt", sep=" ")
    tab1 = pd.read_csv("../bayesgraphs/main1.txt", sep=" ")

    translator = Translator()
    mbn = MultiNetwork(tresh_yes=0.0)

    for ic, c in enumerate(tab.columns):
        # c = "nace"
        print(f"{ic} / {tab.shape[1]} ) {c}")
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

            recos = mbn.predict_all(translations_by_bn, flag_noisy=True, target_variables={c},
                                    flag_translate_output=False, flag_with_nos=True, flag_assume_full=True)
            # exit()
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
        f_exp1 = Counter(tab1[c])

        with open("temp.pickle", "wb") as conn:
            pickle.dump((sampled, tab[c]), conn)

        ks = sorted(f_obs.keys() | f_exp.keys())
        f_obs = np.array([f_obs.get(k, 0) for k in ks])
        f_exp = np.array([f_exp.get(k, 0) for k in ks])
        f_exp1 = np.array([f_exp1.get(k, 0) for k in ks])
        print(f_obs, f_exp, f_exp1)
        f1 = accuracy_score(tab[c], sampled)

        pval = chisquare(f_obs, f_exp=f_exp, ddof=int(len(f_obs) / 2 - 1), axis=0).pvalue
        pval1 = chisquare(f_exp1, f_exp=f_exp, ddof=int(len(f_obs) / 2 - 1), axis=0).pvalue

        a = f_obs - f_exp
        b = f_exp1 - f_exp
        metric = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

        # if len(f_obs) > 3:
        #     continue
        # assert f1 > 1 / max(len(f_obs), len(f_exp)) and (pval > 0.01 or pval / pval1 > 0.5), f"pval={pval}, pval1={pval1}, f1={f1}, dalitajs={max(len(f_obs), len(f_exp))}"
        assert f1 > 0.9 / max(len(f_obs), len(f_exp)) and metric > 0.6, f"pval={pval}, pval1={pval1}, metric={metric}, f1={f1}, dalitajs={max(len(f_obs), len(f_exp))}"



def check_seperate_bn_simulation():
    translator = Translator()
    mbn = MultiNetwork()
    for bn_name, bn in mbn.bns.items():
        pvals = {}
        if bn_name != "main":
            tab = pd.read_csv(f"../bayesgraphs/{bn_name}.txt", sep=" ")
            bn.tresh_yes = 0.0
            for c in tab.columns:
                # if c != 'channel':
                #     continue
                other_columns = list(tab.columns)
                other_columns.remove(c)
                sampled = []
                for i, row in tab.iterrows():
                    list_evidence = set()
                    for k, v in row.items():
                        if k != c:
                            list_evidence.add((k, v))
                    recos = bn.predict_popup(list_evidence, flag_with_nos=True, flag_noisy=True, targets=[c])
                    for varname, value in recos:
                        if varname == c:
                            sampled.append(value)
                f_obs = Counter(sampled)
                f_exp = Counter(tab[c])
                if len(f_obs) < 3:
                    continue
                # print(f_obs, f_exp)
                l1 = list(tab[c])
                l2 = list(sampled)

                ks = sorted(f_obs.keys() | f_exp.keys())
                f_obs = np.array([f_obs.get(k, 0) for k in ks])
                f_exp = np.array([f_exp.get(k, 0) for k in ks])
                # f_obs = f_obs / np.sum(f_obs)
                # f_exp = f_exp / np.sum(f_exp)
                # f1 = f1_score(tab[c], sampled, average='macro')
                f1 = accuracy_score(tab[c], sampled)
                pvals[c] = chisquare(f_obs, f_exp=f_exp, ddof=int(len(f_obs) / 2), axis=0).pvalue
                # print(confusion_matrix(l1, l2, labels=[_[0] for _ in f_obs.most_common()]))
                # print(pvals[c] > 0.05, f1 > 1 / max(len(f_obs), len(f_exp)))
                # print(c)
                # assert pvals[c] > 0.005 and f1 > 1 / max(len(f_obs), len(f_exp)), f"pval={pvals[c]}, f1={f1}, dalitajs={max(len(f_obs), len(f_exp))}"
                assert f1 > 1 / max(len(f_obs), len(f_exp)), f"pval={pvals[c]}, f1={f1}, dalitajs={max(len(f_obs), len(f_exp))}"

# check_seperate_bn_simulation()
check_main_together_with_translations()