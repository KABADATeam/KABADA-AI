import numpy as np
import pysmile
from os.path import join
import pandas as pd
from collections import defaultdict
# pysmile_license is your license key
import smile_licence.pysmile_license
from config import net_dir, epsilon, path_temp_data_file
from collections import Counter
import logging
from copy import deepcopy
from itertools import chain
from Translator import Translator, Flattener
from BeamSearch import Beam, beam_search

class BayesNetwork:
    def __init__(self, path, tresh_yes=0.5):
        self.tresh_yes = tresh_yes
        self.net = pysmile.Network()
        # print("Importing net:", path)
        logging.info("Importing net: " + path)
        self.net.read_file(path)
        self.net.update_beliefs()
        self.net.set_zero_avoidance_enabled(True)

    def learn(self, path_newdata, flag_verbose=-1):
        ds = pysmile.learning.DataSet()
        ds.read_file(path_newdata)
        matching = ds.match_network(self.net)
        em = pysmile.learning.EM()

        list_noisy_max = [node for node in self.net.get_all_nodes()
                          if self.net.get_node_type(node) == pysmile.NodeType.NOISY_MAX]

        for node in list_noisy_max:
            self.net.set_node_type(node, int(pysmile.NodeType.CPT))

        try:
            em.learn(ds, self.net, matching)
        except pysmile.SMILEException as e:
            if "ErrNo=-43" in str(e):
                if flag_verbose==0:
                    print(f"Warning: somewhere in the net is singularities, zeros")
            else:
                raise e

        for node in list_noisy_max:
            self.net.set_node_type(node, int(pysmile.NodeType.NOISY_MAX))

    def learn_new_dependencies(self, path_newdata):
        ds = pysmile.learning.DataSet()
        ds.read_file(path_newdata)
        net_new = pysmile.learning.BayesianSearch().learn(ds)
        # net_new = pysmile.learning.TAN().learn(ds)

        for node in self.net.get_all_nodes():
            parents_new = {*net_new.get_parents(node)}
            print(parents_new)
            if len(parents_new) > 0:
                parents = {*self.net.get_parents(node)}
                print(len(parents_new), len(parents))

                exit()



        print(net_new)
        exit()

    def add_evidence(self, varname, val, flag_verbose=-1, flag_update_beliefs=True):
        try:
            self.net.set_evidence(varname, val)
        except pysmile.SMILEException as e:
            if "ErrNo=-26" in str(e):
                if flag_verbose==0:
                    print(f"Warning: not possible to add {varname} = {val}, value is not possible according to other evidence")
            else:
                raise e
        if flag_update_beliefs:
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

    def get_node_probs(self, node):
        if not self.net.is_value_valid(node):
            self.net.update_beliefs()
        return self.net.get_node_value(node)

    def get_node_iterator(self, list_evidence=None):
        set_fixed_variables = set()
        if list_evidence is not None:
            for varname, value in list_evidence:
                self.add_evidence(varname, value, flag_update_beliefs=False)
                set_fixed_variables.add(varname)

        nodes = []
        for node in self.net.get_all_nodes():
            if len(self.net.get_parents(node)) == 0:
                nodes.append(node)

        # putting nodes in a sequence of causality
        levels_of_nodes = []
        while len(nodes) > 0:
            num_nodes_at_start = len(nodes)
            levels_of_nodes.append([_ for _ in nodes if _ not in set_fixed_variables])
            for node in nodes[:num_nodes_at_start]:
                for child in self.net.get_children(node):
                    if child not in nodes:
                        nodes.append(child)
            nodes = nodes[num_nodes_at_start:]
        return chain(*levels_of_nodes)

    def predict_popup(self, list_evidence=None, flag_with_nos=False, flag_noisy=False, num_beams=1):
        nodes = self.get_node_iterator(list_evidence)
        if num_beams > 1:
            pairs = beam_search(self, nodes, flag_noisy, num_beams)
        else:
            # greedy approach
            pairs = []
            for i_node, node in enumerate(nodes):
                probs = self.get_node_probs(node)
                if flag_noisy:
                    i = np.digitize(np.random.uniform(), np.cumsum(probs))
                else:
                    i = np.argmax(probs)
                val = self.net.get_outcome_id(node, i)
                if probs[i] > self.tresh_yes:
                    pairs.append((self.net.get_node_name(node), val))
                self.net.set_evidence(node, val)

        if not flag_with_nos:
            pairs = [(varname, value) for varname, value in pairs if value != "no"]

        self.clear_evidence()
        return pairs

    def clear_evidence(self, varname=None):
        if varname is None:
            self.net.clear_all_evidence()
        else:
            self.net.clear_evidence(varname)

    def generate_one_sample(self, flag_with_nos=False, num_beams=1):
        return self.predict_popup(flag_with_nos=flag_with_nos, flag_noisy=True, num_beams=num_beams)


class MultiNetwork:
    def __init__(self, translator=None, tresh_yes=0.5):
        self.tresh_yes = tresh_yes
        self.translator = Translator()
        self.flattener = None
        self.bns = {}
        self.random_variables_2_predict = {}

        if translator is not None:
            self.random_variables_2_predict = {bn_name: [_ for _ in vars.keys() if _!="is_added"] for bn_name, vars in translator.inverse_lookup.items()}

        for bn_name in self.translator.inverse_lookup.keys():
            self.add_net(bn_name)

    def add_net(self, bn_name):
        if bn_name not in self.bns:
            self.bns[bn_name] = BayesNetwork(join(net_dir, bn_name + ".xdsl"), tresh_yes=self.tresh_yes)
            if bn_name not in self.random_variables_2_predict:
                self.random_variables_2_predict[bn_name] = [_ for _ in self.bns[bn_name].get_node_names() if _!="is_added"]

    def add_evidence(self, bn_name, list_evidence):
        # if two identical evidence provided - there will be smile error
        list_evidence = {*list_evidence}
        self.bns[bn_name].clear_evidence()
        for varname, value in list_evidence:
            self.bns[bn_name].add_evidence(varname, value)

    def clear_evidence(self, bn_name, list_evidence):
        for evidence in list_evidence:
            for varname, value in evidence.items():
                self.bns[bn_name].clear_evidence(varname)

    def learn_all(self, tabs_by_bn, min_size_training_set=10):
        for bn_name, tab in tabs_by_bn.items():

            if tab.shape[0] < min_size_training_set:
                continue

            if bn_name in self.bns:
                for varname in self.bns[bn_name].get_node_names():
                    if varname not in tab.columns:
                        tab[varname] = ['no'] * tab.shape[0]
                tab.to_csv(path_temp_data_file, sep=" ", index=False)
                self.bns[bn_name].learn(path_temp_data_file)

    def sample_all(self):
        bp = []
        for bn_name, bn in self.bns.items():
            for _ in range(np.random.randint(1, 3)):
                recomendations = bn.generate_one_sample()
                bp.append((bn_name, recomendations, None))
        translations_by_bn = self.translator.back(bp)

        if self.flattener is None:
            self.flattener = Flattener()
        bp = self.flattener.back(translations_by_bn)
        return bp

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
            recomendations = {*self.bns[bn_name].predict_popup(list_evidence)}
            bp.append((bn_name, recomendations, id_bp))
            self.bns[bn_name].clear_evidence()

        translations_by_bn = self.translator.back(bp)

        return translations_by_bn


if __name__ == "__main__":
    from pprint import pprint
    from tests.body_generators import PredictBodyGen
    from Translator import Flattener, BPMerger

    def check_recomendation_generation():
        np.random.seed(1)
        gen = PredictBodyGen()
        flattener = Flattener()
        merger = BPMerger()
        net = MultiNetwork()
        np.random.seed(1)

        for _ in range(100):
            np.random.seed(_)
            # bp = gen.generate_from_bn()
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

    def single_bn_train_test():
        # np.random.seed(0)
        from config import path_temp_data_file
        # mbn = MultiNetwork(tresh_yes=0.0)
        # bn = mbn.bns["consumer_segments"]
        # bn = BayesNetwork("bayesgraphs/business_plan.xdsl", tresh_yes=0.0)
        bn = BayesNetwork("bayesgraphs/age_vs_edu.xdsl", tresh_yes=0.0)
        # bn = BayesNetwork("bayesgraphs/business_plan_with_noisy_max.xdsl")
        bps = defaultdict(list)
        B = 100
        all_varnames = bn.get_node_names()
        for _ in range(B):
            for varname, value in bn.generate_one_sample(flag_with_nos=True):
                bps[varname].append(value)

        # deleting some columns
        # for i, c in enumerate(list(bps.keys())):
        #     del bps[c]
        #     if i > 0:
        #         break

        for node in bn.get_node_names():
            if node not in bps:
                bps[node] = ["no"] * B

        pd.DataFrame(bps).to_csv(path_temp_data_file, sep=" ", index=False)
        # bn.learn(path_temp_data_file)
        bn.learn_new_dependencies(path_temp_data_file)
        # bn.learn("bayesgraphs/consumer_segments.txt")
        exit()

    # check_recomendation_generation()
    # generate_bn_sample()
    single_bn_train_test()
