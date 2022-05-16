import json
from glob import glob
from os.path import join, basename
from config import repo_dir, path_generated_list_of_autocompletable_variables
from pprint import pprint
from collections import defaultdict
from copy import deepcopy


def copy_attribute(bp_from, bp_to, attr_name='id'):
    if isinstance(bp_from, dict):
        assert isinstance(bp_to, dict)
        res = {}
        if attr_name in bp_from:
            bp_to[attr_name] = bp_from[attr_name]

        for k in bp_from.keys() & bp_to.keys():
            copy_attribute(bp_from[k], bp_to[k], attr_name=attr_name)
        return res

    if isinstance(bp_from, list):
        assert isinstance(bp_to, list)
        for bp_from_sub, bp_to_sub in zip(bp_from, bp_to):
            copy_attribute(bp_from_sub, bp_to_sub, attr_name=attr_name)


def rec_add_attribute(bp, path, bp_name_where, attr_name='id', attr_value="", sep="::"):

    if isinstance(bp, dict):
        if path == bp_name_where:
            bp[attr_name] = attr_value

        for k, v in bp.items():
            if len(path) > 0:
                rec_add_attribute(v, path + sep + k, bp_name_where, attr_name=attr_name, attr_value=attr_value, sep=sep)
            else:
                rec_add_attribute(v, k, bp_name_where, attr_name=attr_name, attr_value=attr_value, sep=sep)

    if isinstance(bp, list):
        for v in bp:
            rec_add_attribute(v, path, bp_name_where, attr_name=attr_name, attr_value=attr_value, sep=sep)


def add_attribute(bp, bp_name_where, attr_name='id', attr_value="", sep="::"):
    rec_add_attribute(bp, "", bp_name_where, attr_name=attr_name, attr_value=attr_value, sep=sep)


def rec_merge(bp1, bp2, path, bp2bn, sep="::"):

    if isinstance(bp1, dict):
        res = {}
        for k in bp1.keys() & bp2.keys():
            path1 = k if len(path) == 0 else path + sep + k
            res[k] = rec_merge(bp1[k], bp2[k], path1, bp2bn, sep=sep)

        for k in bp1.keys() - bp2.keys():
            res[k] = bp1[k]

        for k in bp2.keys() - bp1.keys():
            res[k] = bp2[k]

        return res

    if isinstance(bp1, list):
        res = bp1 + bp2
        return res


class BPMerger:
    def __init__(self):
        with open(join(repo_dir, "docs", "bp_flatten_names_to_bns.json"), "r") as conn:
            self.bp2bn = json.load(conn)

    def __call__(self, bp1, bp2):
        return rec_merge(bp1, bp2, "", self.bp2bn, sep="::")


def rec_accumulate_guids(bp, path, guids, bp2bn, sep="::"):
    if isinstance(bp, str) or isinstance(bp, int) or isinstance(bp, float) or isinstance(bp, bool):
        guids.append(path + sep + str(bp))

    if isinstance(bp, dict):
        for k, v in bp.items():
            if len(path) > 0:
                rec_accumulate_guids(v, path + sep + k, guids, bp2bn, sep=sep)
            else:
                rec_accumulate_guids(v, k, guids, bp2bn, sep=sep)

    if isinstance(bp, list):
        for v in bp:
            if path in bp2bn:
                subguids = []
                rec_accumulate_guids(v, path, subguids, bp2bn, sep=sep)
                if len(subguids) > 0:
                    guids.append((bp2bn[path], subguids, v.get('id', None)))
            else:
                rec_accumulate_guids(v, path, guids, bp2bn, sep=sep)


def rec_delete_missing(bp, path, set_guids, sep="::"):
    # print(path, bp)
    if isinstance(bp, dict):
        for k in tuple(bp.keys()):
            v = bp[k]
            if isinstance(v, str) or isinstance(v, int) or isinstance(v, float) or isinstance(v, bool):
                if sep.join(path + [str(v)]) not in set_guids:
                    del bp[k]
            else:
                rec_delete_missing(v, path + [k], set_guids, sep=sep)
                if len(bp[k]) == 0:
                    del bp[k]

    if isinstance(bp, list):
        inds_drop = []
        elements_to_add = []
        for i in range(len(bp)):
            if isinstance(bp[i], str) or isinstance(bp[i], int) or isinstance(bp[i], float) or isinstance(bp[i], bool):
                guid_from_full_bp = sep.join(path + [str(bp[i])])
                if guid_from_full_bp[-1] == "*":
                    path_join = sep.join(path) + "::"
                    for guid in set_guids:
                        if path_join in guid:
                            elements_to_add.append(guid.replace(path_join, ""))

                if guid_from_full_bp not in set_guids:
                    inds_drop.append(i)
            else:
                rec_delete_missing(bp[i], path, set_guids, sep=sep)
                if len(bp[i]) == 0:
                    inds_drop.append(i)

        for i in reversed(sorted(inds_drop)):
            bp.pop(i)
        bp.extend(elements_to_add)

class Flattener:
    def __init__(self, sep="::"):
        self.sep = sep
        with open(join(repo_dir, "docs", "full_bp.json"), "r") as conn:
            self.full_bp = json.load(conn)

        self.merger = BPMerger()

        with open(join(repo_dir, "docs", "bp_flatten_names_to_bns.json"), "r") as conn:
            self.bp2bn = json.load(conn)
        self.bn2bp = {v: k for k, v in self.bp2bn.items()}

    def __call__(self, bp, flag_generate_plus_one=False, id_bp=None):
        guids = []
        rec_accumulate_guids(bp, "", guids, self.bp2bn)
        output = []
        default = []
        for guid in guids:
            if isinstance(guid, tuple):
                output.append(guid)
            else:
                default.append(guid)
        if flag_generate_plus_one:
            for bn_name in {_[0] for _ in output}:
                output.append((bn_name, [], "sample"))

        if id_bp is None:
            output.append(("plan", default, bp.get('id', None)))
        else:
            output.append(("plan", default, id_bp))
        return output

    def back_one_recomendation(self, guids):
        set_guids = set(guids)
        bp = deepcopy(self.full_bp)
        rec_delete_missing(bp, [], set_guids, sep=self.sep)
        return bp

    def back(self, recomendations_by_bn):
        bp = None
        for bn_name, recomendations, id_bp in recomendations_by_bn:
            bp_new = self.back_one_recomendation(recomendations)
            if id_bp is not None:
                id_bp = None if id_bp == "sample" else id_bp
                add_attribute(bp_new, self.bn2bp[bn_name], attr_name="id", attr_value=id_bp)

            if bp is None:
                bp = bp_new
            else:
                bp = self.merger(bp, bp_new)
        return bp


def is_bps_identical(bp1, bp2, flattener=None):
    if flattener is None:
        flattener = Flattener()

    f1 = flattener(bp1)
    f2 = flattener(bp2)

    if len(f1) != len(f2):
        return False

    f1 = sorted(f1, key=lambda x: x[0] + str(x[2]))
    f2 = sorted(f2, key=lambda x: x[0] + str(x[2]))

    for (bpname1, guids1, id_bp1), (bpname2, guids2, id_bp2) in zip(f1, f2):
        if bpname1 != bpname2:
            return False
        if set(guids1) != set(guids2) and bpname1 != 'plan':
            # print(set(guids1))
            # print(set(guids2))
            # print(222222)
            return False
        if id_bp1 != id_bp2:
            return False
    return True


class Translator:
    def __init__(self):
        fs = sorted(glob(join(repo_dir, "translation", "*.json")))

        with open(path_generated_list_of_autocompletable_variables, "r") as conn:
            self.dict_binary_nodes = json.load(conn)
            for k in self.dict_binary_nodes.keys():
                self.dict_binary_nodes[k] = {*self.dict_binary_nodes[k]}

        self.lookup = {}
        for f in fs:
            bn_name = basename(f).replace(".json", "")
            if bn_name not in self.dict_binary_nodes:
                self.dict_binary_nodes[bn_name] = set()

            with open(f, "r") as conn:
                translation = json.load(conn)

            for guid, trans in translation.items():
                for _, kw_dicts in trans.items():
                    pairs = set()
                    for kw_dict in kw_dicts:
                        for varname, value in kw_dict.items():
                            pairs.add((varname, value))
                    self.lookup[guid] = (bn_name, pairs)

        self.inverse_lookup = defaultdict(lambda: defaultdict(list))
        for guid, (bn_name, pairs) in self.lookup.items():
            for varname, value in pairs:
                self.inverse_lookup[bn_name][varname].append(value)

    def __call__(self, bag_guids, flag_assume_full=False, *args, **kwargs):
        translation = defaultdict(set)
        for guid in bag_guids:
            if guid in self.lookup:
                bn_name, evidence = self.lookup[guid]
                translation[bn_name].update(evidence)

        if flag_assume_full:
            for bn_name in translation.keys():
                for varname in self.dict_binary_nodes[bn_name] - {_[0] for _ in translation[bn_name]}:
                    translation[bn_name].add((varname, 'no'))

        return translation

    def back(self, bp, flag_dont_check_bn_name=False):
        guids_by_bn = []
        for bn_name0, values0, id_bp in bp:
            guids = []
            for guid, (bn_name, necessary_condition) in self.lookup.items():
                if bn_name == bn_name0 or flag_dont_check_bn_name:
                    if necessary_condition.issubset(values0):
                        guids.append(guid)
            guids_by_bn.append((bn_name0, guids, id_bp))
        return guids_by_bn


if __name__ == "__main__":
    flattener = Flattener()
    print(flattener({
        "a": {"a1": ["a11", "a12"], "a2": ["a21", "a22"]},
        "b": {"b1": ["b11"], "b2": ["b21", "b22", "b23"]},
    }))
    translator = Translator()
