import numpy as np
import pysmile
import os
from os.path import join
import pandas as pd
from collections import defaultdict
import smile_licence.pysmile_license
from config import net_dir, epsilon, path_temp_data_file
from collections import Counter
import logging
from copy import deepcopy
from pprint import pprint
from itertools import chain
from Translator import Translator, Flattener
from BeamSearch import beam_search


class BayesNetwork:
    def __init__(self, path, tresh_yes=0.5):
        self.tresh_yes = tresh_yes
        self.net = pysmile.Network()
        logging.info("Importing net: " + path)
        self.net.read_file(path)

        for node in self.net.get_all_nodes():
            current_node_type = self.net.get_node_type(node)
            self.net.set_node_type(node, int(pysmile.NodeType.CPT))

            n_vals = self.net.get_outcome_count(node)
            cpt = np.asarray(self.net.get_node_definition(node)).reshape(-1, n_vals)
            cpt[cpt < epsilon] = epsilon
            for i in range(cpt.shape[0]):
                s = np.sum(cpt[i, :])
                if s == 0:
                    cpt[i, :] = np.ones((n_vals,)) / n_vals
                else:
                    cpt[i, :] = cpt[i, :] / s
            self.net.set_node_definition(node, list(cpt.flatten()))
            self.net.set_node_type(node, current_node_type)

        self.net.set_zero_avoidance_enabled(True)
        self.net.update_beliefs()

    def learn(self, path_newdata, flag_verbose=-1):
        ds = pysmile.learning.DataSet()
        ds.read_file(path_newdata)
        matching = ds.match_network(self.net)
        em = pysmile.learning.EM()

        list_noisy_max = [(node, self.net.get_node_type(node)) for node in self.net.get_all_nodes()
                          if self.net.get_node_type(node) != pysmile.NodeType.CPT]

        for node, _ in list_noisy_max:
            self.net.set_node_type(node, int(pysmile.NodeType.CPT))

        try:
            em.learn(ds, self.net, matching)
        except pysmile.SMILEException as e:
            if "ErrNo=-43" in str(e):
                if flag_verbose==0:
                    print(f"Warning: somewhere in the net is singularities, zeros")
            else:
                raise e

        for node, node_type in list_noisy_max:
            self.net.set_node_type(node, node_type)

    def learn_new_dependencies(self, path_newdata, flag_verbose=-1):
        ds = pysmile.learning.DataSet()
        ds.read_file(path_newdata)
        net_new = pysmile.learning.BayesianSearch().learn(ds)
        # net_new = pysmile.learning.TAN().learn(ds)
        # net_new.write_file("temp.xdsl")
        # net_new.read_file("temp.xdsl")

        for node in self.net.get_all_nodes():
            node_type = self.net.get_node_type(node)
            if node_type != pysmile.NodeType.CPT:
                self.net.set_node_type(node, int(pysmile.NodeType.CPT))

            parents_new = {*net_new.get_parents(node)}
            if len(parents_new) > 0:
                parents = {*self.net.get_parents(node)}
                for parent in parents_new - parents:
                    if node not in self.net.get_parents(parent):
                        parent_type = self.net.get_node_type(parent)
                        if parent_type != pysmile.NodeType.CPT:
                            self.net.set_node_type(parent, int(pysmile.NodeType.CPT))

                        self.net.add_arc(parent, node)

                        if parent_type != pysmile.NodeType.CPT:
                            self.net.set_node_type(parent, parent_type)

            if node_type != pysmile.NodeType.CPT:
                self.net.set_node_type(node, node_type)

        self.learn(path_newdata, flag_verbose=flag_verbose)

    def add_evidence(self, varname, val, flag_verbose=-1, flag_update_beliefs=True):

        if isinstance(val, list):
            if len(val) > 0:
                valnames = self.net.get_outcome_ids(varname)
                probs = np.zeros((len(valnames),))
                for i, valname in enumerate(valnames):
                    if valname in val:
                        probs[i] += 1.0
                probs = probs / np.sum(probs)
                self.net.set_virtual_evidence(varname, list(probs))
        else:
            # print(varname, val, self.net.get_outcome_ids(varname))
            try:
                self.net.set_evidence(varname, val)
            except pysmile.SMILEException as e:
                if "ErrNo=-26" in str(e) or "ErrNo=-2" in str(e):
                    if flag_verbose == 0:
                        print(
                            f"Warning: not possible to add {varname} = {val}, value is not possible according to other evidence")
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

    def get_node_iterator(self, list_evidence=None, targets=None):
        set_fixed_variables = set()
        if list_evidence is not None:
            for varname, value in list_evidence:
                set_fixed_variables.add(varname)

        nodes = []
        for node in self.net.get_all_nodes():
            if len(self.net.get_parents(node)) == 0:
                nodes.append(node)

        # putting nodes in a sequence of causality
        levels_of_nodes = []
        while len(nodes) > 0:
            num_nodes_at_start = len(nodes)
            if targets is None:
                levels_of_nodes.append([_ for _ in nodes if _ not in set_fixed_variables])
            else:
                levels_of_nodes.append([_ for _ in nodes
                                        if (_ not in set_fixed_variables) and self.net.get_node_name(_) in targets])

            for node in nodes[:num_nodes_at_start]:
                for child in self.net.get_children(node):
                    if child not in nodes:
                        nodes.append(child)
            nodes = nodes[num_nodes_at_start:]
        return chain(*levels_of_nodes)

    def predict_popup(self, list_evidence=None, flag_with_nos=False, flag_noisy=False, num_beams=1, targets=None):

        if list_evidence is not None:
            for varname, value in list_evidence:
                self.add_evidence(varname, value, flag_update_beliefs=False)

        nodes = self.get_node_iterator(list_evidence, targets)
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

        self.add_net("main")

    def add_net(self, bn_name):
        if bn_name not in self.bns:
            if os.path.exists(join(net_dir, bn_name + "_trained.xdsl")):
                self.bns[bn_name] = BayesNetwork(join(net_dir, bn_name + "_trained.xdsl"), tresh_yes=self.tresh_yes)
            else:
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

    def learn_all(self, tabs_by_bn, min_size_training_set=10, flag_verbose=0):
        for bn_name, tab in tabs_by_bn.items():

            if tab.shape[0] < min_size_training_set:
                continue

            if bn_name in self.bns:
                for varname in self.bns[bn_name].get_node_names():
                    if varname not in tab.columns:
                        tab[varname] = ['no'] * tab.shape[0]
                tab.to_csv(path_temp_data_file, sep=" ", index=False)
                flag_bn_search_failed = False
                try:
                    self.bns[bn_name].learn_new_dependencies(path_temp_data_file)
                except pysmile.SMILEException as e:
                    flag_bn_search_failed = True
                    if "ErrNo=-1" in str(e):
                        if flag_verbose == 0:
                            print(e)
                    else:
                        raise e
                if flag_bn_search_failed:
                    self.bns[bn_name].learn(path_temp_data_file)
                self.bns[bn_name].net.write_file(f"{net_dir}/trained_graphs/{bn_name}_trained.xdsl")

    def sample_all(self, mode="seperately"):
        if mode == "seperately":
            bp = []
            for bn_name, bn in self.bns.items():
                for _ in range(np.random.randint(1, 3)):
                    recomendations = bn.generate_one_sample()
                    bp.append((bn_name, recomendations, None))

        elif mode == "main":
            # TODO izmantojot main
            raise NotImplemented

        translations_by_bn = self.translator.back(bp)
        if self.flattener is None:
            self.flattener = Flattener()
        bp = self.flattener.back(translations_by_bn)
        return bp

    def predict_all(self, guids_by_bn, location=None):
        bp = []

        other_guids_by_bn = defaultdict(set)
        other_guids_by_id = {}
        print(guids_by_bn)
        for bn_name, list_guids, id_bp in guids_by_bn:
            if len(list_guids) > 0:
                if id_bp is not None:
                    other_guids_by_id[id_bp] = (bn_name, {*list_guids})
                other_guids_by_bn[bn_name].update(list_guids)

        for bn_name, list_guids, id_bp in guids_by_bn:
            # looking for some BFF
            dict_guids_bffs = defaultdict(set)
            for potential_id in list_guids:
                potential_id = potential_id.split("::")[-1]
                if potential_id in other_guids_by_id:
                    dict_guids_bffs[other_guids_by_id[potential_id][0]].update(other_guids_by_id[potential_id][1])

            dict_evidence = defaultdict(list)
            for other_bn_name, other_guids in other_guids_by_bn.items():
                if other_bn_name != bn_name:
                    print(111111111111111111111111111111111111111111111111111111)
                    # print(other_guids)

                    # if any BFF found it gets special care
                    if other_bn_name in dict_guids_bffs:
                        list_evidence = self.translator(dict_guids_bffs[other_bn_name])
                    else:
                        list_evidence = self.translator(other_guids)
                    if len(list_evidence) == 0:
                        continue
                    print(other_bn_name, list_evidence.keys())

                    assert len(list_evidence) == 1, "pa tiikliem tika sadaliits ar flattener"

                    for varname, value in list_evidence[other_bn_name]:
                        dict_evidence[varname].append(value)

            for varname, values in dict_evidence.items():
                values = values[0] if len(values) == 1 else values
                self.bns["main"].add_evidence(varname, values, flag_update_beliefs=False)

            list_evidence = self.translator(list_guids)
            if len(list_evidence) == 0:
                if bn_name in self.bns:
                    recomendations = self.bns[bn_name].generate_one_sample()
                    bp.append((bn_name, recomendations, id_bp))
                continue
            assert len(list_evidence) == 1, "pa tiikliem tika sadaliits ar flattener"

            list_evidence = list_evidence[bn_name]
            target_names = {*self.bns[bn_name].get_node_names()}

            recomendations = {*self.bns["main"].predict_popup(list_evidence, targets=target_names)}

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
            bp = gen.generate_from_bn()
            # bp = gen()
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
        mbn = MultiNetwork(tresh_yes=0.0)
        # bn = mbn.bns["consumer_segments"]
        bn = mbn.bns["value_propositions"]
        # bn = BayesNetwork("bayesgraphs/business_plan.xdsl", tresh_yes=0.0)
        # bn = BayesNetwork("bayesgraphs/age_vs_edu.xdsl", tresh_yes=0.0)
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

    check_recomendation_generation()
    # generate_bn_sample()
    # single_bn_train_test()
