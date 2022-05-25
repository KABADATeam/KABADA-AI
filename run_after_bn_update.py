from tests.translation_test import *
from config import path_generated_list_of_autocompletable_variables
import json
from collections import defaultdict
import os
from Translator import rec_delete_missing
mbn = MultiNetwork()

def generate_dict_autocompletable_variables():

    dict_autocompletable_variables = {}
    for node in mbn.bns['main'].net.get_all_nodes():
        outcomes = {*mbn.bns['main'].net.get_outcome_ids(node)}
        if "no" in outcomes:
            varname = mbn.bns['main'].net.get_node_name(node)
            for bn_name, bn in mbn.bns.items():
                if bn_name != "main":
                    if varname in bn.get_node_names():
                        break
            if bn_name in dict_autocompletable_variables:
                dict_autocompletable_variables[bn_name].append(varname)
            else:
                dict_autocompletable_variables[bn_name] = [varname]
            del varname

    flag_has_updates = True
    if os.path.exists(path_generated_list_of_autocompletable_variables):
        with open(path_generated_list_of_autocompletable_variables, "r") as conn:
            dict_autocompletable_variables_prev = json.load(conn)

        if dict_autocompletable_variables_prev.keys() == dict_autocompletable_variables.keys():
            flag_has_updates = False
            for k in dict_autocompletable_variables_prev.keys():
                if {*dict_autocompletable_variables_prev[k]} != {*dict_autocompletable_variables[k]}:
                    flag_has_updates = True
                    break

    if flag_has_updates:
        with open(path_generated_list_of_autocompletable_variables, "w") as conn:
            json.dump(dict_autocompletable_variables, conn)


def generate_dict_bp_relation_keys_for_training():

    dict_childkey2parentkey = {}
    for bn_name, kvs in mbn.sub_bn_relations.items():
        for parent, relation in kvs.items():
            childkey = mbn.flattener.bn2bp[bn_name] + "::" + relation[1]
            parentkey = mbn.flattener.bn2bp[parent] + "::id"
            dict_childkey2parentkey[childkey] = parentkey
            break


    pprint(dict_childkey2parentkey)
    exit()


# generate_dict_bp_relation_keys_for_training()

generate_dict_autocompletable_variables()

###### TESTS
check_predict_endpoint()
check_variable_names_in_translations()
check_correct_binary_variable_detection()
check_sub_bn_cnts()
check_bp_flatten_names_to_bns()
no_translation_same_key()
check_translations_or_bns_not_missing()
check_variable_names()
validate_wrt_texter()
check_if_all_nets_in_main()
check_all_translationalble_guids_in_full_bp()
check_recomendation_generation()
generate_bn_sample()
# check_bp_flattener()
print("tests passed - everythings OK :)")


