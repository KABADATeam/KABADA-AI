import numpy as np
import pysmile
from os.path import join
from collections import defaultdict
# pysmile_license is your license key
import smile_licence.pysmile_license
from config import net_dir, epsilon

class BayesNetwork:
    def __init__(self, path):
        self.net = pysmile.Network()
        print("Importing net:", path)
        self.net.read_file(path)

    def learn(self, path_newdata):
        ds = pysmile.learning.DataSet()
        ds.read_file(path_newdata)
        matching = ds.match_network(self.net)
        em = pysmile.learning.EM()
        em.learn(ds, self.net, matching)

    def add_evidence(self, varname, val):
        self.net.set_evidence(varname, val)
        self.net.update_beliefs()

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
    def __init__(self):
        self.bns = {}

    def add_net(self, bn_name):
        if bn_name not in self.bns:
            self.bns[bn_name] = BayesNetwork(join(net_dir, bn_name + ".xdsl"))

    def add_evidence(self, bn_name, list_evidence):
        for evidence in list_evidence:
            for varname, value in evidence.items():
                self.bns[bn_name].add_evidence(varname, value)

    def clear_evidence(self, bn_name, list_evidence):
        for evidence in list_evidence:
            for varname, value in evidence.items():
                self.bns[bn_name].clear_evidence(varname)

    def predict(self, bn_name, list_evidence):
        # TODO handlot joint varbuutiibu vektoram
        preds = defaultdict(lambda: 1.0)
        for evidence in list_evidence:
            for varname, value in evidence.items():
                val, prob = self.bns[bn_name].predict_popup(varname)
                preds[val] += np.clip(prob, epsilon, np.inf)
        best_val = None
        best_prob = 0.0
        for val, prob in preds.items():
            if prob > best_prob:
                best_prob = prob
                best_val = val
        return best_val, best_prob
