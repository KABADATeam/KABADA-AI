import numpy as np
import pysmile
from os.path import join
from collections import defaultdict
# pysmile_license is your license key
import smile_licence.pysmile_license
from config import net_dir, epsilon
from collections import Counter
import logging
from Translator import Translator

class BayesNetwork:
    def __init__(self, path):

        self.net = pysmile.Network()
        # print("Importing net:", path)
        logging.info("Importing net: " + path)
        self.net.read_file(path)
        self.net.update_beliefs()

    def learn(self, path_newdata):
        ds = pysmile.learning.DataSet()
        ds.read_file(path_newdata)
        matching = ds.match_network(self.net)
        em = pysmile.learning.EM()
        em.learn(ds, self.net, matching)

    def add_evidence(self, varname, val):
        self.net.set_evidence(varname, val)
        self.net.update_beliefs()

    def get_node_names(self):
        h = self.net.get_first_node()
        names = []
        while True:
            names.append(self.net.get_node_name(h))
            h = self.net.get_next_node(h)
            if h == -1:
                break
        return names

    def predict_popup(self, varname):
        # TODO uztaisiit arii ja varname ir vektors, tad kāda ir joint varbūtība vektoram
        probs = self.net.get_node_value(varname)
        i_most_likely = np.argmax(probs)
        return self.net.get_outcome_id(varname, i_most_likely), probs[i_most_likely]

    def clear_evidence(self, varname=None):
        if varname is None:
            self.net.clear_all_evidence()
        else:
            self.net.clear_evidence(varname)


class MultiNetwork:
    def __init__(self, translator=None):
        self.translator = Translator()
        self.bns = {}
        self.random_variables_2_predict = {}
        if translator is not None:
            self.random_variables_2_predict = {bn_name: list(vars.keys()) for bn_name, vars in translator.inverse_lookup.items()}

    def add_net(self, bn_name):
        if bn_name not in self.bns:
            self.bns[bn_name] = BayesNetwork(join(net_dir, bn_name + ".xdsl"))
            if bn_name not in self.random_variables_2_predict:
                self.random_variables_2_predict[bn_name] = self.bns[bn_name].get_node_names()

    def add_evidence(self, bn_name, list_evidence):
        # if two identical evidence provided - there will be smile error
        list_evidence = {(list(b.keys())[0], list(b.values())[0]) for b in list_evidence}
        for varname, value in list_evidence:
            for _ in range(10):
                try:
                    self.bns[bn_name].add_evidence(varname, value)
                    # print('success')
                except Exception as e:
                    # print('fail')
                    pass

    def clear_evidence(self, bn_name, list_evidence):
        for evidence in list_evidence:
            for varname, value in evidence.items():
                self.bns[bn_name].clear_evidence(varname)

    def predict_all(self, guids_by_bn):
        # TODO handlot multi value guids (lai prob buutu joint)
        bp = []
        for bn_name, list_guids in guids_by_bn:
            list_evidence = self.translator(list_guids)
            if len(list_evidence) == 0:
                continue
            assert len(list_evidence) == 1 , "pa tiikliem tika sadaliits ar flattener"
            list_evidence = list_evidence[bn_name]

            self.add_net(bn_name)
            self.add_evidence(bn_name, list_evidence)

            list_variables = self.random_variables_2_predict[bn_name]
            s_variables_in_evidence = {list(b.keys())[0] for b in list_evidence}
            recomendations = set()
            for varname in list_variables:
                if varname not in s_variables_in_evidence:
                    try:
                        val, prob = self.bns[bn_name].predict_popup(varname)
                        if prob > 0.5:
                            recomendations.add((varname, val))
                    except Exception as e:
                        # print(varname, e)
                        pass

            bp.append((bn_name, recomendations))
            self.bns[bn_name].clear_evidence()

        translations_by_bn = self.translator.back(bp)

        return translations_by_bn


if __name__ == "__main__":
    from pprint import pprint
    from tests.body_generators import PredictBodyGen
    from Translator import Flattener, BPMerger

    gen = PredictBodyGen()
    flattener = Flattener()
    merger = BPMerger()
    net = MultiNetwork()

    for _ in range(100):
        bp = gen()
        guids_by_bn = flattener(bp)
        recomendations_by_bn = net.predict_all(guids_by_bn)

        bp = None
        for bn_name, recomendations in recomendations_by_bn:
            if bp is None:
                bp = flattener.back(recomendations)
            else:
                bp = merger(bp, flattener.back(recomendations))
        print(bp)
        exit()


