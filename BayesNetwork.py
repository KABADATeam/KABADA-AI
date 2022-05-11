import numpy as np
import pysmile
import os
from os.path import join
import pandas as pd
from collections import defaultdict
import smile_licence.pysmile_license
from config import net_dir, epsilon, path_temp_data_file, repo_dir
from collections import Counter
import logging
import json
from copy import deepcopy
from pprint import pprint
from itertools import combinations
from uuid import uuid4
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
            # self.net.set_node_type(node, int(pysmile.NodeType.CPT))

            n_vals = self.net.get_outcome_count(node)
            cpt = np.asarray(self.net.get_node_definition(node)).reshape(-1, n_vals)
            cpt[cpt < epsilon] = epsilon
            for i in range(cpt.shape[0]):
                s = np.sum(cpt[i, :])
                if s == 0:
                    cpt[i, :] = np.ones((n_vals,)) / n_vals
                else:
                    cpt[i, :] = cpt[i, :] / s
            # if node == 6:
            #     print(cpt.flatten(), len(cpt.flatten()), current_node_type)
            self.net.set_node_definition(node, list(cpt.flatten()))
            # self.net.set_node_type(node, current_node_type)

        for node in self.net.get_all_nodes():
            probs = np.array(self.net.get_node_definition(node)).flatten()
            # print(node, probs, len(probs))
            assert np.sum(probs == 0) == 0

        self.net.set_zero_avoidance_enabled(True)
        self.net.update_beliefs()

    def _bp1_conditioned_likelihood_of_bp2(self, bp1, bp2, varnames):
        likelihoods = []
        for ivar, varname in enumerate(varnames):
            if ivar == 0:
                likelihood = float(bp1[ivar] == bp2[ivar])
            else:
                # values = self.net.get_outcome_ids(varname)
                probs = self.get_node_probs(varname)
                likelihood = probs[bp2[ivar]]
                # print(varname, bp1[ivar], probs)
            self.add_evidence(varname, bp1[ivar])
            likelihoods.append(likelihood)
        return likelihoods

    def distance(self, bp1, bp2, targets=None, flag_simple_dist=True):
        """"induced distance between two business plans"""
        nodes = list(self.get_node_iterator(targets=targets))
        varnames = [self.net.get_node_name(node) for node in nodes]
        # print(2222, varnames)
        bp1 = {k: v for k, v in bp1}
        bp2 = {k: v for k, v in bp2}
        bp1 = [self.net.get_outcome_ids(varname).index(bp1[varname]) for varname in varnames]
        bp2 = [self.net.get_outcome_ids(varname).index(bp2[varname]) for varname in varnames]
        if flag_simple_dist:
            return sum((a == b for a, b in zip(bp1, bp2))) / len(bp1)
        likelihoods1 = self._bp1_conditioned_likelihood_of_bp2(bp1, bp2, nodes)
        self.clear_evidence(nodes)
        likelihoods2 = self._bp1_conditioned_likelihood_of_bp2(bp2, bp1, nodes)
        # print(likelihoods1)
        # print(likelihoods2)
        return np.average(likelihoods1 + likelihoods2)

    def learn(self, path_newdata, flag_verbose=0):
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

        dict_node2name_new = {node: net_new.get_node_name(node) for node in net_new.get_all_nodes()}
        dict_name2node_old = {self.net.get_node_name(node): node for node in self.net.get_all_nodes()}

        for node_new in net_new.get_all_nodes():
            node = dict_name2node_old[dict_node2name_new[node_new]]
            node_type = self.net.get_node_type(node)
            if node_type != pysmile.NodeType.CPT:
                self.net.set_node_type(node, int(pysmile.NodeType.CPT))

            parents_new = {dict_name2node_old[dict_node2name_new[node]] for node in net_new.get_parents(node_new)}
            if len(parents_new) > 0:
                parents = {*self.net.get_parents(node)}
                for parent in parents_new - parents:
                    if node not in self.net.get_parents(parent):
                        parent_type = self.net.get_node_type(parent)
                        if parent_type != pysmile.NodeType.CPT:
                            self.net.set_node_type(parent, int(pysmile.NodeType.CPT))

                        try:
                            self.net.add_arc(parent, node)
                        except pysmile.SMILEException as e:
                            if "ErrNo=-11" in str(e):
                                if flag_verbose == 0:
                                    print(f"Warning: not adding arc, becaause of cycle")
                            else:
                                raise e

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
            set_fixed_variables.update((varname for varname, value in list_evidence))

        nodes = filter(lambda node:
                       self.net.get_node_name(node) not in set_fixed_variables,
                       self.net.get_all_nodes())

        if targets is not None:
            nodes = filter(lambda node:
                           self.net.get_node_name(node) in targets,
                           nodes)

        return nodes

    def predict_popup(self, list_evidence=None, flag_with_nos=False, flag_noisy=False, num_beams=1, targets=None,
                      flag_return_all_beams=False):

        if list_evidence is not None:
            for varname, value in list_evidence:
                self.add_evidence(varname, value, flag_update_beliefs=False)

        nodes = self.get_node_iterator(list_evidence, targets)
        nodes = list(nodes)
        if num_beams > 1:
            pairs = beam_search(self, nodes, flag_noisy, num_beams, flag_return_all_beams=flag_return_all_beams)
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
                self.net.set_evidence(node, i)

        if not flag_with_nos:
            if flag_return_all_beams:
                if num_beams == 1:
                    pairs = [pairs]
                for i, subpairs in enumerate(pairs):
                    pairs[i] = [(varname, value) for varname, value in subpairs if value != "no"]
            else:
                pairs = [(varname, value) for varname, value in pairs if value != "no"]

        self.clear_evidence()
        return pairs

    def clear_evidence(self, varname=None):
        if varname is None:
            self.net.clear_all_evidence()
        else:
            if not isinstance(varname, list):
                varname = [varname]
            for _ in varname:
                self.net.clear_evidence(_)

    def generate_one_sample(self, flag_with_nos=False, num_beams=1):
        return self.predict_popup(flag_with_nos=flag_with_nos, flag_noisy=True, num_beams=num_beams)


class MultiNetwork:
    def __init__(self, translator=None, tresh_yes=0.5, flattener=None):
        self.tresh_yes = tresh_yes

        self.translator = translator
        if translator is None:
            self.translator = Translator()

        self.flattener = flattener
        if flattener is None:
            self.flattener = Flattener()

        self.bns = {}
        self.sampling_order = ["value_propositions", "consumer_segments", "business_segments", "public_bodies_and_ngo",
                               "channels", "get_new_customers", "keep_customers", "convince_existing_to_spend_more",
                               "revenue_streams_consumers", "revenue_streams_business", "revenue_streams_ngo",
                               "key_partners_distributors", "key_partners_suppliers",
                               "key_partners_others", "fixed_costs", "variable_costs"]

        with open(join(repo_dir, "docs", "sub_bn_relations.json"), "r") as conn:
            self.sub_bn_relations = json.load(conn)
            for child in list(self.sub_bn_relations.keys()):
                relations = {}
                for kw in self.sub_bn_relations[child]:
                    for parent, relation in kw.items():
                        relations[parent] = relation
                self.sub_bn_relations[child] = relations

        for bn_name in self.translator.inverse_lookup.keys():
            self.add_net(bn_name)

        self.add_net("main")
        self.set_only_main_variables = {*self.bns['main'].get_node_names()}.difference(
            chain(*(bn.get_node_names() for bn_name, bn in self.bns.items() if bn_name != 'main')))

    def add_net(self, bn_name):
        if bn_name not in self.bns:
            if os.path.exists(join(net_dir, bn_name + "_trained.xdsl")):
                self.bns[bn_name] = BayesNetwork(join(net_dir, bn_name + "_trained.xdsl"), tresh_yes=self.tresh_yes)
            else:
                self.bns[bn_name] = BayesNetwork(join(net_dir, bn_name + ".xdsl"), tresh_yes=self.tresh_yes)

    def add_evidence(self, bn_name, list_evidence):
        # if two identical evidence provided - there will be smile error
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
                # for varname in self.bns[bn_name].get_node_names():
                #     if varname not in tab.columns:
                #         tab[varname] = ['no'] * tab.shape[0]
                for c in tab.columns:
                    if len({*tab[c]}) == 1:
                        del tab[c]
                tab.drop_duplicates(inplace=True)
                # for c in tab.columns:
                #     counter = Counter(tab[c])
                #     print(c, counter, len(counter))

                if tab.shape[0] < 4 or tab.shape[1] < 2:
                    print("no data")
                    return

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

    def sample_all(self, mode="main"):
        if mode == "seperately":
            bp = []
            for bn_name, bn in self.bns.items():
                for _ in range(np.random.randint(1, 3)):
                    recomendations = bn.generate_one_sample()
                    bp.append((bn_name, recomendations, None))

        elif mode == "main":

            bp = self.predict_all([("swot", [], None)], flag_noisy=True, target_bns=["swot"],
                                              flag_assume_full=True, num_beams=5, flag_clear_evidence=False)

            # sagjeneree guids_by_bn formaa
            for bn_name in self.sampling_order:
                num_node_name = "num_" + bn_name

                if not self.bns['main'].net.is_value_valid(num_node_name):
                    self.bns['main'].net.update_beliefs()

                probs = self.bns['main'].net.get_node_value(num_node_name)

                i = np.digitize(np.random.uniform(), np.cumsum(probs))
                outcome = self.bns['main'].net.get_outcome_id(num_node_name, i)
                outcome = outcome.replace("num", "")
                n = int(np.random.randint(5, 20) if outcome == "_more" else outcome)
                n = 1 if n == 0 else n

                if bn_name in self.sub_bn_relations:
                    dict_parents_by_name = defaultdict(list)
                    for parent, _ in self.sub_bn_relations[bn_name].items():
                        for bn_name1, list_guids, id_bp in bp:
                            if bn_name1 == parent:
                                dict_parents_by_name[parent].append((id_bp, list_guids))

                    bp_new = []
                    if len(dict_parents_by_name) > 0:
                        for parent, id_and_guids_bps in dict_parents_by_name.items():
                            id_bps, list_guids = zip(*id_and_guids_bps)

                            relation_type, field_name = self.sub_bn_relations[bn_name][parent]
                            field_name = f"{self.flattener.bn2bp[bn_name]}::{field_name}"
                            if relation_type == "1_to_n":
                                # TODO refaktorizeet so, un iztesteet mehaanismu
                                n = int(np.clip(n, max(1, int(len(id_bps) / 2)), len(id_bps)))
                                parent_group_dists = []
                                num_per_group = (len(id_bps) // n)
                                if num_per_group >= 2:
                                    inds_bps = list(range(len(id_bps)))
                                    for inds_bps_subset in combinations(inds_bps, num_per_group):
                                        ds = []
                                        for i0, i1 in combinations(inds_bps_subset, 2):
                                            bp0 = self.translator(list_guids[i0], flag_assume_full=True)[parent]
                                            bp1 = self.translator(list_guids[i1], flag_assume_full=True)[parent]
                                            ds.append(self.bns[parent].distance(bp0, bp1))
                                        if np.min(ds) > 0.8:
                                            parent_group_dists.append((inds_bps_subset, np.min(ds)))

                                    parent_group_dists = sorted(parent_group_dists, key=lambda d: -d[1])

                                uuid = str(uuid4())
                                # parent_group_dists = parent_group_dists[:1]
                                for inds_bps_subset, _ in parent_group_dists[:n]:
                                    bp_new.append((bn_name,
                                                   [f"{field_name}::{id_bps[ind_bp]}" for ind_bp in inds_bps_subset]
                                                   + [f"{self.flattener.bn2bp[bn_name]}::id::{uuid}"],
                                                   uuid))

                                if len(parent_group_dists) < n:
                                    for ind_bp in range(n - len(parent_group_dists)):
                                        bp_new.append((bn_name,
                                                       [f"{field_name}::{id_bps[ind_bp]}",
                                                        f"{self.flattener.bn2bp[bn_name]}::id::{uuid}"],
                                                       uuid))

                            elif self.sub_bn_relations[bn_name][parent] == "1_to_1":
                                raise NotImplemented
                            elif self.sub_bn_relations[bn_name][parent] == "n_to_1":
                                raise NotImplemented
                            else:
                                raise ValueError
                else:
                    bp_new = []
                    for _ in range(n):
                        uuid = str(uuid4())
                        bp_new.append((bn_name,
                                       [f"{self.flattener.bn2bp[bn_name]}::id::{uuid}"],
                                       uuid))

                # TODO visus tukšos ar vienu un to pashu parenta id_bp generet ar beam search garantejot to atskiribu
                bp_monte_carlo = self.predict_all(bp + bp_new, flag_noisy=True, target_bns=[bn_name],
                                                  flag_assume_full=True, num_beams=5, flag_clear_evidence=False)

                for i in range(len(bp_new)):
                    bn_name, list_parent_ids, id_bp = bp_new[i]
                    _, list_guids, _ = bp_monte_carlo[i]
                    bp_new[i] = bn_name, list_parent_ids + list_guids, id_bp

                bp.extend((_ for _ in bp_new if len(_[1]) > 0))

        # print(1111, sorted({*self.bns.keys()}.difference(set((_[0] for _ in bp)))))
        self.bns['main'].clear_evidence()
        return bp

    def predict_all(self, guids_by_bn, flag_noisy=False, target_bns=None, target_variables=None,
                    flag_translate_output=True, flag_with_nos=False, flag_assume_full=False,
                    num_beams=1, flag_clear_evidence=True):
        bp = []
        other_guids_by_id = {}
        other_guids_by_bn = defaultdict(set)
        for bn_name, list_guids, id_bp in guids_by_bn:
            if len(list_guids) > 0:
                if id_bp is not None:
                    other_guids_by_id[id_bp] = (bn_name, {*list_guids})
                other_guids_by_bn[bn_name].update(list_guids)

        for bn_name, list_guids, id_bp in guids_by_bn:
            if bn_name not in self.bns:
                continue
            if target_bns is not None:
                if bn_name not in target_bns:
                    continue

            # looking for some BFF
            dict_guids_bffs = defaultdict(set)
            for potential_id in list_guids:
                potential_id = potential_id.split("::")[-1]
                if potential_id in other_guids_by_id:
                    dict_guids_bffs[other_guids_by_id[potential_id][0]].update(other_guids_by_id[potential_id][1])

            dict_evidence = defaultdict(list)
            for other_bn_name, other_guids in other_guids_by_bn.items():
                if other_bn_name != bn_name:

                    # if any BFF found it gets special care
                    if other_bn_name in dict_guids_bffs:
                        list_evidence = self.translator(dict_guids_bffs[other_bn_name])
                    else:
                        list_evidence = self.translator(other_guids)
                    if len(list_evidence) == 0:
                        continue
                    assert len(list_evidence) == 1, "pa tiikliem tika sadaliits ar flattener"

                    for varname, value in list_evidence[other_bn_name]:
                        dict_evidence[varname].append(value)

            for varname, values in dict_evidence.items():
                values = values[0] if len(values) == 1 else values
                self.bns["main"].add_evidence(varname, values, flag_update_beliefs=False)

            list_evidence = self.translator(list_guids, flag_assume_full=flag_assume_full)
            assert len(list_evidence) <= 1, "pa tiikliem tika sadaliits ar flattener"
            list_evidence = list_evidence[bn_name]
            target_names = {*self.bns[bn_name].get_node_names()}
            if target_variables is not None:
                target_names = (target_names | self.set_only_main_variables) & target_variables
            list_evidence = {_ for _ in list_evidence if _[0] not in target_names}
            # print(bn_name, len(list_evidence), len(self.bns[bn_name].get_node_names()))
            recomendations = {*self.bns["main"].predict_popup(list_evidence, targets=target_names,
                                                              flag_noisy=flag_noisy, flag_with_nos=flag_with_nos,
                                                              num_beams=num_beams)}
            bp.append((bn_name, recomendations, id_bp))
            if flag_clear_evidence:
                self.bns["main"].clear_evidence()

        if not flag_translate_output:
            return bp
        translations_by_bn = self.translator.back(bp)
        return translations_by_bn


def check_recomendation_generation():
    from tests.body_generators import PredictBodyGen
    np.random.seed(1)
    gen = PredictBodyGen()
    flattener = Flattener()
    net = MultiNetwork()
    np.random.seed(1)
    for _ in range(100):
        np.random.seed(_)
        guids_by_bn = gen.generate_from_bn()
        # bp = gen()
        # guids_by_bn = flattener(bp)
        recomendations_by_bn = net.predict_all(guids_by_bn)

def generate_bn_sample():
    mnt = MultiNetwork()
    for _ in range(100):
        translations_by_bn = mnt.sample_all()
        bp = mnt.flattener.back(translations_by_bn)
    # pprint(bp)
    # exit()


if __name__ == "__main__":
    from pprint import pprint
    from Translator import Flattener, BPMerger

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
    generate_bn_sample()
    # single_bn_train_test()
