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
    def __init__(self, path, tresh_yes=0.5):
        self.tresh_yes = tresh_yes
        self.net = pysmile.Network()
        # print("Importing net:", path)
        logging.info("Importing net: " + path)
        self.net.read_file(path)
        self.net.update_beliefs()
        self.net.set_zero_avoidance_enabled(True)

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

    def generate_one_sample(self):
        # self.add_evidence("is_added", "yes")
        nodes = []
        for node in self.net.get_all_nodes():
            if len(self.net.get_parents(node)) == 0:
                nodes.append(node)
        pairs = set()
        while len(nodes) > 0:
            num_nodes_at_start = len(nodes)
            for node in nodes[:num_nodes_at_start]:
                if self.net.get_node_name(node) != "is_added":
                    # print(self.net.get_node_name(node))
                    if not self.net.is_value_valid(node):
                        self.net.update_beliefs()
                    probs = self.net.get_node_value(node)
                    probs = np.cumsum(probs)
                    i = np.digitize(np.random.uniform(), probs)
                    val = self.net.get_outcome_id(node, i)
                    if val != "no":
                        pairs.add((self.net.get_node_name(node), val))
                    self.net.set_evidence(node, val)
                    self.net.clear_evidence(node)

                for child in self.net.get_children(node):
                    if child not in nodes:
                        nodes.append(child)

            nodes = nodes[num_nodes_at_start:]

        self.clear_evidence()
        return pairs


class MultiNetwork:
    def __init__(self, translator=None, tresh_yes=0.5):
        self.tresh_yes = tresh_yes
        self.translator = Translator()
        self.bns = {}
        self.random_variables_2_predict = {}
        if translator is not None:
            self.random_variables_2_predict = {bn_name: [_ for _ in vars.keys() if _!="is_added"] for bn_name, vars in translator.inverse_lookup.items()}

    def add_net(self, bn_name):
        if bn_name not in self.bns:
            self.bns[bn_name] = BayesNetwork(join(net_dir, bn_name + ".xdsl"), tresh_yes=self.tresh_yes)
            if bn_name not in self.random_variables_2_predict:
                self.random_variables_2_predict[bn_name] = [_ for _ in self.bns[bn_name].get_node_names() if _!="is_added"]

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
        for bn_name, list_guids, id_bp in guids_by_bn:

            list_evidence = self.translator(list_guids)

            if len(list_evidence) == 0:
                if bn_name in self.bns:
                    recomendations = self.bns[bn_name].generate_one_sample()
                    bp.append((bn_name, recomendations, id_bp))
                continue
            assert len(list_evidence) == 1, "pa tiikliem tika sadaliits ar flattener"
            list_evidence = list_evidence[bn_name]

            self.add_net(bn_name)
            # print(bn_name)
            # print(111, bn_name, len(self.bns[bn_name].generate_one_sample()))
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
                    except pysmile.SMILEException as e:
                        pass

            bp.append((bn_name, recomendations, id_bp))
            self.bns[bn_name].clear_evidence()

        translations_by_bn = self.translator.back(bp)

        return translations_by_bn


if __name__ == "__main__":
    from pprint import pprint
    from tests.body_generators import PredictBodyGen
    from Translator import Flattener, BPMerger

    def check_recomendation_generation():
        gen = PredictBodyGen()
        flattener = Flattener()
        merger = BPMerger()
        net = MultiNetwork()

        for _ in range(100):
            bp = gen()
            guids_by_bn = flattener(bp)
            recomendations_by_bn = net.predict_all(guids_by_bn)

            # pprint(bp)
            # exit()
        print(recomendations_by_bn)


    def generate_bn_sample():
        net = BayesNetwork(join(net_dir, "consumer_segments.xdsl"))
        net.generate_one_sample()
        exit()

    check_recomendation_generation()
    # generate_bn_sample()
