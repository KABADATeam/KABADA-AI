import pandas as pd
from config import path_temp_data_file
from collections import Counter
from pprint import pprint
from Translator import Translator, Flattener, is_bps_identical
from BayesNetwork import MultiNetwork

translator = Translator()
flattener = Flattener()


def swot_example():

    bp_input = {'plan': {'swot': {'opportunities': ['cdc1a197-fb79-42b9-a7cb-9ff8fd0e1622'],
                                  'strengths': ['42c22ecb-1f79-467a-8b1f-2e709de5a5e2',
                                                '7d1df83e-9bdd-47eb-8fad-ad7f7b1a8329'],
                                  'threats': ['f611bf2d-3089-4e53-b362-cf740f1f102a'],
                                  'weaknesses': ['e93d16a1-fc41-4443-b88b-023d051103bf']}}}

    recos_by_bn = flattener(bp_input, flag_generate_plus_one=True)

    for i in range(len(recos_by_bn)):
        bn_name, list_guids, id_bn = recos_by_bn[i]
        bn_k = 'swot' if bn_name == 'plan' else bn_name
        recos_by_bn[i] = bn_name, translator(list_guids)[bn_k], id_bn

    # pprint(recos_by_bn)
    # exit()

    # recos_by_bn = [
    #     ('plan',
    #      {
    #          ('guarantees_and_warranties', 'strength'),
    #          ('operational_processes', 'strength'),
    #          ('economic_growth', 'opportunity'),
    #          ("accessibility_of_financial_resources", "threat"),
    #          ("advertising_pr_and_sales_promotion", "weakness")
    #      },
    #      None)
    # ]

    translations_by_bn = translator.back(recos_by_bn)
    reco = flattener.back(translations_by_bn)
    pprint(translations_by_bn)
    pprint(reco)
    print(is_bps_identical(reco, bp_input))


def swot_generation_example():
    mbn = MultiNetwork()
    pairs = mbn.bns['swot'].generate_one_sample()
    recos_by_bn = [('plan', pairs, None)]
    translations_by_bn = translator.back(recos_by_bn)
    reco = flattener.back(translations_by_bn)
    # pprint(translations_by_bn)
    pprint(reco)
    # pprint(mbn.bns['swot'].generate_one_sample())

swot_generation_example()