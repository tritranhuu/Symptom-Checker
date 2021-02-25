from deepcare.bayesian_network.model import DC_Bayesian_Network
from deepcare.database.query import DC_Query

from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
from pgmpy.readwrite import BIFWriter

import numpy as np
import pandas as pd

from configs import data_file

def get_node_possibility(node_name, list_node_name_P, list_node_name_N, solver):
    dict_node_name = {}
    dict_node_name_P = {key: 1 for key in list_node_name_P}
    dict_node_name_N = {key: 0 for key in list_node_name_N}
    dict_node_name.update(dict_node_name_P)
    dict_node_name.update(dict_node_name_N)

    phi_query = solver.query(variables = [node_name], evidence = dict_node_name)
    prob_node_name = phi_query.values
    prob_node_name_true = prob_node_name[1]
    return prob_node_name_true

def get_node_ranking_posibility(list_node_name, list_node_name_P, list_node_name_N, solver):
    list_prob_node_name = []
    for i in range (len(list_node_name)):
        result = get_node_possibility(list_node_name[i], list_node_name_P, list_node_name_N, solver)
        list_prob_node_name.append(result)
    list_prob_node_name.sort(reverse=True)
    return list_prob_node_name

if __name__ == "__main__":

    query = DC_Query(data_file.APP_ONTOLOGY)

    bayesian = DC_Bayesian_Network(query, disease_group="Bệnh hệ hô hấp", proportion_dir=data_file.APP_PROPORTION_DIR)
    model = bayesian.build()

    print(model.check_model())
    print(bayesian.symptom_disease_dict.keys())
    solver = VariableElimination(model)
    print("querying")
    result = solver.query(variables=["<http://deepcare.io/2213353c_05c7_4071_a75d_6771b874e060>"], evidence={"Age":0, "Gender":0, "<http://deepcare.io/0d48b52f_99af_42cd_8c14_167c9913e8b7>":1})
    print(result)
    print("querying 2")
    result = solver.query(variables=["<http://deepcare.io/2213353c_05c7_4071_a75d_6771b874e060>"], evidence={"Age":0, "Gender":0, "<http://deepcare.io/0d48b52f_99af_42cd_8c14_167c9913e8b7>":1})
    print(result)
    
    #writer = BIFWriter(model)
    #writer.write_bif("bayes.bif")
