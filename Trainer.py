import numpy as np
from pprint import pprint
from tests.body_generators import PredictBodyGen
from BayesNetwork import MultiNetwork
from Translator import Translator, Flattener
from collections import defaultdict, Counter
import pandas as pd
from itertools import product, chain
import pysmile
import pickle
import logging
from config import path_temp_data_file, net_dir


def sample_permutations(guids_by_bn, mbn):
    autocompletable = set(chain(*mbn.translator.dict_binary_nodes.values()))

    childkey2parentkey = []
    for bn_name, kvs in mbn.sub_bn_relations.items():
        for parent, relation in kvs.items():
            childkey = mbn.flattener.bn2bp[bn_name] + "::" + relation[1]
            parentkey = mbn.flattener.bn2bp[parent] + "::id"
            childkey2parentkey.append((
                childkey + "::",
                parentkey + "::"
            ))
            break
    set_childkey2parentkey = set(chain(*childkey2parentkey))
    # guids_by_bn = flattener(guids_by_bn)
    # print(guids_by_bn)
    # print(sorted({*mbn.bns.keys()}.difference(set((_[0] for _ in guids_by_bn)))))
    # exit()
    row_common_only_in_bn = {
        "num_" + bn_name: f"num{cnt}" if cnt < 5 else "num_more"
        for bn_name, cnt in Counter((_[0] for _ in guids_by_bn if _[0] != "plan")).items()
    }

    bnname2bns = defaultdict(list)

    max_per_bn_name = 2
    max_perms_generate = 10000
    # pprint(guids_by_bn)

    for bn_name, guids, id_bp in guids_by_bn:
        if len(bnname2bns[bn_name]) < max_per_bn_name:
            bnname2bns[bn_name].append(guids)

    n_perms = np.prod([len(v) for v in bnname2bns.values()])

    data_entries = []
    for iperm, guids in enumerate(product(*bnname2bns.values())):
        if iperm == max_perms_generate:
            break
        guids = list(chain(*guids))
        flag_subbn_associations_are_correct = True
        for childkey, parentkey in childkey2parentkey:
            child = None
            parent = None
            for guid in guids:
                if childkey in guid:
                    child = guid.replace(childkey, "")
                if parentkey in guid:
                    parent = guid.replace(parentkey, "")
                if parent is not None and child is not None:
                    break

            # xor
            # pprint(guids)
            # print(childkey, parentkey)
            # print(parent, child)
            assert not (child is not None and parent is None)
            # assert (parent is not None and child is not None) or (parent is None and child is None)
            flag_subbn_associations_are_correct = parent == child
            if not flag_subbn_associations_are_correct:
                break

        if flag_subbn_associations_are_correct:

            # not adding child/parent associations
            clean_guids = []
            for guid in guids:
                flag_add = True
                for k in set_childkey2parentkey:
                    if k in guid:
                        flag_add = False
                        break
                if flag_add:
                    clean_guids.append(guid)

            row = {}
            for bn_name, pairs in mbn.translator(clean_guids).items():
                for varname, value in pairs:
                    row[varname] = value
            row.update(row_common_only_in_bn)

            for varname in autocompletable.difference(row.keys()):
                row[varname] = 'no'
            data_entries.append(row)

    return data_entries


class Trainer:
    def __init__(self, mbn=None):
        if mbn is None:
            mbn = MultiNetwork()
        self.mbn = mbn
        self.flattener = Flattener()
        self.translator = Translator()
        self.bps_for_training = []

    def add_bp(self, bp):
        self.bps_for_training.append(bp)

    def search_new_arcs(self, path_newdata, flag_verbose=-1):
        flag_successfull = True
        ds = pysmile.learning.DataSet()
        ds.read_file(path_newdata)
        net_new = pysmile.learning.BayesianSearch().learn(ds)
        # net_new = pysmile.learning.TAN().learn(ds)
        # net_new.write_file("temp.xdsl")
        # net_new.read_file("temp.xdsl")
        bn = self.mbn.bns["main"]
        dict_node2name_new = {node: net_new.get_node_name(node) for node in net_new.get_all_nodes()}
        dict_name2node_old = {bn.net.get_node_name(node): node for node in bn.net.get_all_nodes()}

        for node_new in net_new.get_all_nodes():
            node = dict_name2node_old[dict_node2name_new[node_new]]
            node_type = bn.net.get_node_type(node)
            if node_type != pysmile.NodeType.CPT:
                bn.net.set_node_type(node, int(pysmile.NodeType.CPT))

            parents_new = {dict_name2node_old[dict_node2name_new[node]] for node in net_new.get_parents(node_new)}
            if len(parents_new) > 0:
                parents = {*bn.net.get_parents(node)}
                for parent in parents_new - parents:
                    if node not in bn.net.get_parents(parent):
                        parent_type = bn.net.get_node_type(parent)
                        if parent_type != pysmile.NodeType.CPT:
                            bn.net.set_node_type(parent, int(pysmile.NodeType.CPT))

                        try:
                            bn.net.add_arc(parent, node)
                        except pysmile.SMILEException as e:
                            flag_successfull = False
                            if "ErrNo=-11" in str(e):
                                if flag_verbose == 0:
                                    print(f"Warning: not adding arc, becaause of cycle")
                            elif "ErrNo=-1" in str(e):
                                if flag_verbose == 0:
                                    print(e)
                            else:
                                raise e

                        if parent_type != pysmile.NodeType.CPT:
                            bn.net.set_node_type(parent, parent_type)

            if node_type != pysmile.NodeType.CPT:
                bn.net.set_node_type(node, node_type)
        return flag_successfull

    def learn_parameters(self, path_newdata, flag_verbose=-1):
        flag_successfull = True
        bn = self.mbn.bns["main"]

        ds = pysmile.learning.DataSet()
        ds.read_file(path_newdata)
        matching = ds.match_network(bn.net)
        em = pysmile.learning.EM()

        list_noisy_max = [(node, bn.net.get_node_type(node)) for node in bn.net.get_all_nodes()
                          if bn.net.get_node_type(node) != pysmile.NodeType.CPT]

        for node, _ in list_noisy_max:
            bn.net.set_node_type(node, int(pysmile.NodeType.CPT))

        try:
            em.learn(ds, bn.net, matching)
        except pysmile.SMILEException as e:
            flag_successfull = False
            if "ErrNo=-43" in str(e):
                if flag_verbose == 0:
                    print(f"Warning: somewhere in the net is singularities, zeros")
            else:
                raise e

        for node, node_type in list_noisy_max:
            bn.net.set_node_type(node, node_type)
        return flag_successfull

    def train(self, min_size_training_set=5, flag_verbose=0):

        data_entries = []
        for bp in self.bps_for_training:
            subdata_entries = sample_permutations(bp, self.mbn)
            data_entries.extend(subdata_entries)
        tab = pd.DataFrame(data_entries)

        for c in tab.columns:
            uni_vals = {*tab[c]}

            if len(uni_vals) == 1:
                del tab[c]
                logging.warning(f"dropping {c} because have just one value")

            if np.nan in uni_vals:
                if c in self.mbn.translator.dict_binary_nodes:
                    tab[c][pd.isna(tab[c])] = "no"
                    logging.warning(f"autocompleting {c} because of missing values")
                else:
                    del tab[c]
                    logging.warning(f"dropping {c} because of missing values")

        tab.drop_duplicates(inplace=True)
        # for c in tab.columns:
        #     counter = Counter(tab[c])
        #     print(c, counter, len(counter))

        if tab.shape[0] < min_size_training_set or tab.shape[1] < 2:
            print("no data")
            return

        tab.to_csv(path_temp_data_file, sep=" ", index=False)

        flag_arc_search_ok = self.search_new_arcs(path_temp_data_file)
        logging.info(f"flag_arc_search_ok = {flag_arc_search_ok}")
        flag_parameter_estim_ok = self.learn_parameters(path_temp_data_file)
        logging.info(f"flag_parameter_estim_ok = {flag_parameter_estim_ok}")
        if flag_parameter_estim_ok:
            self.mbn.bns["main"].net.write_file(f"{net_dir}/trained_graphs/main_trained.xdsl")
        else:
            self.mbn.reload()


def check_training():
    from Translator import is_bps_identical
    from itertools import combinations
    from tests.body_generators import PredictBodyGen
    flattener = Flattener()
    mbn = MultiNetwork(tresh_yes=0.5)

    trainer = Trainer()
    generator = PredictBodyGen()
    bps = []
    for seed in range(30):
        np.random.seed(seed)
        # guids_by_bn = mbn.sample_all()
        guids_by_bn = generator.generate_from_bn()
        bp = flattener.back(guids_by_bn)
        bps.append(bp)
        guids_by_bn = flattener(bp)
        trainer.add_bp(guids_by_bn)
    # with open("temp.pickle", "wb") as conn:
    #     pickle.dump(bps, conn)

    # with open("temp.pickle", "rb") as conn:
    #     bps = pickle.load(conn)
    # for bp in bps:
    #     guids_by_bn = flattener(bp)
    #     trainer.add_bp(guids_by_bn)

    # exit()
    for bp1, bp2 in combinations(bps, 2):
        assert not is_bps_identical(bp1, bp2, mbn.flattener)

    mbn.reload(flag_use_trained=False)
    trainer.train()


if __name__ == "__main__":
    check_training()