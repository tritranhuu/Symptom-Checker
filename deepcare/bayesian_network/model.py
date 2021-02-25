import pandas as pd
import numpy as np
import pickle as pkl

import os

from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination

from deepcare.database.query import DC_Query
from configs import data_file 


class DC_Bayesian_Network():

    def __init__(self, query, disease_group=None, proportion_dir=None):
        self.model = None
        self.query = query
        with open(data_file.APP_SYMPTOMS_DATA_VI, 'rb') as handle:
            self.symptoms = pkl.load(handle)
        with open(data_file.APP_DISEASES_DATA_VI, 'rb') as handle:
            self.diseases = pkl.load(handle)
        
        self.disease_field = list(self.diseases.keys())
        if disease_group != None:
            self.disease_field = self.query.get_diseases_by_group_iri(disease_group)
        self.symptom_disease_dict = self.create_symptom_disease_dict()
        key_to_del = []
        for k, v in self.symptom_disease_dict.items():
            if len(v) > 10:
                key_to_del.append(k)
        for k in key_to_del:
            self.symptom_disease_dict.pop(k)

        for filename in os.listdir(proportion_dir):
            disease_iri = 'http://deepcare.io/' + filename.split("_")[0]
            self.fill_proportion_from_files_disease(proportion_dir+filename, disease_iri)
        
        print(len(self.disease_field))
        print(len(self.symptom_disease_dict))
        
    def create_symptom_disease_dict(self):
        self.symptom_disease_dict = {}  
        for disease, data in self.diseases.items():
            if disease not in self.disease_field:
                continue
            for symptom in data.symptoms:
                if symptom in ["<http://deepcare.io/RDcMMpjCSnJXbSb1xHoxW2R>", "<http://deepcare.io/dd0113c8_ae5a_4ca6_b645_27e1091afa1d>"]:
                    continue
                item = {
                    "disease": disease,
                    "proportion": 0.5
                }
                if symptom in self.symptom_disease_dict.keys():
                    if item not in self.symptom_disease_dict[symptom]:
                        self.symptom_disease_dict[symptom].append(item)
                else:
                    self.symptom_disease_dict[symptom] = [item]
            
            for symptom in data.main_symptoms:
                if symptom in ["<http://deepcare.io/RDcMMpjCSnJXbSb1xHoxW2R>", "<http://deepcare.io/dd0113c8_ae5a_4ca6_b645_27e1091afa1d>"]:
                    continue
                item = {
                    "disease": disease,
                    "proportion": 0.8
                }
                if symptom in self.symptom_disease_dict.keys():
                    if item not in self.symptom_disease_dict[symptom]:
                        self.symptom_disease_dict[symptom].append(item)
                else:
                    self.symptom_disease_dict[symptom] = [item]
            
            for symptom in data.probably_symptoms:
                if symptom in ["<http://deepcare.io/RDcMMpjCSnJXbSb1xHoxW2R>", "<http://deepcare.io/dd0113c8_ae5a_4ca6_b645_27e1091afa1d>"]:
                    continue
                item = {
                    "disease": disease,
                    "proportion": 0.2
                }
                if symptom in self.symptom_disease_dict.keys():
                    if item not in self.symptom_disease_dict[symptom]:
                        self.symptom_disease_dict[symptom].append(item)
                else:
                    self.symptom_disease_dict[symptom] = [item]
        return self.symptom_disease_dict
    
    def create_nodes_and_edges(self):
        for s, _ in self.symptom_disease_dict.items():
            self.model.add_node(s)
        
        for d in self.disease_field:
            self.model.add_node(d)
            self.model.add_edge('Age', d)
            self.model.add_edge('Gender', d)
        #     for symptom in d_data.symptoms + d_data.main_symptoms + d_data.probably_symptoms:
        #         self.model.add_edge(d_label, symptom)
        return self.model

    def fill_proportion_from_files_disease(self, file_path, disease_iri):
        data = pd.read_excel(file_path, header=None)
        if disease_iri not in self.disease_field:
            return
        for i in range(data.count()[0]):
            symptom = data.loc[i][1]
            if data.loc[i][2] < 0 or data.loc[i][2]:
                continue
            else:
                proportion = data.loc[i][2]
            for d in self.symptom_disease_dict[symptom]:
                if d['disease'] == disease_iri:
                    d['proportion'] = proportion
                    continue
        return

    def create_symptom_cpds_table(self, symptom):
        disease_data = self.symptom_disease_dict[symptom]
        num_diseases = len(disease_data)
        
        # print(num_diseases)
        num_rows = np.power(2, num_diseases)
        cpd_list = []
        evidence = [disease_data[i]['disease'] for i in range(num_diseases)]
        for d in evidence:
            self.model.add_edge(d, symptom)
        evidence_card = [2]*len(evidence)
        total_proportion = sum([disease_data[i]['proportion'] for i in range(num_diseases)])
        for i in range(num_rows):
            total_true = 0
            cpd_state = str(bin(i)[2:].zfill(num_diseases))
            # print(cpd_state)
            for state_index in range(num_diseases):
                if cpd_state[state_index] == '0':
                    total_true += disease_data[state_index]['proportion']
            temp_proportion = total_true/total_proportion
            cpd_list.append(temp_proportion)
        cpd_symptom = TabularCPD(symptom, 2, values=[cpd_list, [(1-x) for x in cpd_list]], evidence=evidence, evidence_card=evidence_card)
        self.model.add_cpds(cpd_symptom)
        return self.model


    def create_disease_cpds_table(self, disease):
        disease_age = self.diseases[disease].age
        disease_gender_common = self.diseases[disease].gender_common
        disease_gender_only = self.diseases[disease].gender_only
        
        cpd_disease = TabularCPD(disease, 2, values= [[0.5]*10, [0.5]*10], evidence=['Gender', 'Age'], evidence_card=[2,5]) 
        self.model.add_cpds(cpd_disease)
        return self.model
        
    def build(self):
        self.model = BayesianModel()
        self.model.add_node('Age')
        self.model.add_node('Gender')
        cpd_age = TabularCPD('Age', 5, values=[[0.2], [0.2], [0.2], [0.2], [0.2]])
        cpd_gender = TabularCPD('Gender', 2, values=[[0.5],[0.5]])
        self.model.add_cpds(cpd_age, cpd_gender)
        self.model = self.create_nodes_and_edges()

        for d in self.disease_field:
            self.model = self.create_disease_cpds_table(d)

        for symptom in self.symptom_disease_dict.keys():
            self.model = self.create_symptom_cpds_table(symptom)
        return self.model


class DC_Bayesian_General_Network():
    def __init__(self, query, proportion_dir=None):
        self.model = None
        self.current_model = None
        self.query = query

        with open(data_file.APP_SYMPTOMS_DATA_VI, 'rb') as handle:
            self.symptoms = pkl.load(handle)
        with open(data_file.APP_DISEASES_DATA_VI, 'rb') as handle:
            self.diseases = pkl.load(handle)
        
        self.disease_field = list(self.diseases.keys())
        self.disease_group = query.get_all_disease_groups_iri()
        self.symptom_disease_dict, self.symptom_group_dict = self.create_symptom_dict(query)
        self.very_common_symptoms = []
        key_to_del = []
        symptom_group_iri = query.get_all_symptom_groups_iri()
        for k in symptom_group_iri:
            if k in self.symptom_disease_dict:
                self.symptom_disease_dict.pop(k)
                self.symptom_group_dict.pop(k)
        for k, v in self.symptom_disease_dict.items():
            if len(v) < 10 :
                key_to_del.append(k)
            # if len(v) > 10:
            #     print(len(self.symptom_group_dict[k]))
            #     print(len(v))
        for k, v in self.symptom_group_dict.items():
            if len(v) > 10 :
                key_to_del.append(k)
                self.very_common_symptoms.append(k)
        for k in key_to_del:
            self.symptom_disease_dict.pop(k)
            self.symptom_group_dict.pop(k)
            
        # print(self.symptom_group_dict)
        # print(len(self.symptom_disease_dict))
        # sl = [self.symptoms[s].label for s in self.symptom_disease_dict]
        # print(sl)
        with open("data/pretrained_model/bayesian_network/symptom_disease.pkl", 'wb') as f:
            pkl.dump(self.symptom_disease_dict, f, protocol=pkl.HIGHEST_PROTOCOL)
        with open("data/pretrained_model/bayesian_network/symptom_group.pkl", 'wb') as f:
            pkl.dump(self.symptom_group_dict, f, protocol=pkl.HIGHEST_PROTOCOL)
            

    def create_symptom_dict(self, query):
        try:
            f1 = open("data/pretrained_model/bayesian_network/symptom_disease.pkl", 'rb')
            f2 = open("data/pretrained_model/bayesian_network/symptom_group.pkl", 'rb')
            self.symptom_disease_dict = pkl.load(f1)
            self.symptom_group_dict = pkl.load(f2)
            return self.symptom_disease_dict, self.symptom_group_dict
        except Exception:
            pass
            
        self.symptom_disease_dict = {}
        self.symptom_group_dict = {}
        for disease, data in self.diseases.items():
            for symptom in data.symptoms:
                item = {
                    "disease": disease,
                    "proportion": 0.5
                }
                 
                if symptom in self.symptom_disease_dict.keys():
                    if item not in self.symptom_disease_dict[symptom]:
                        self.symptom_disease_dict[symptom].append(item)
                else:
                    self.symptom_disease_dict[symptom] = [item]
                group = query.get_disease_group_iri_by_iri(disease)
                items_group = self.symptom_group_dict.setdefault(symptom, {})
                self.symptom_group_dict[symptom][group] = self.symptom_group_dict[symptom].setdefault(group, 0) + 0.5
                

            for symptom in data.main_symptoms:
                item = {
                    "disease": disease,
                    "proportion": 0.8
                }
                if symptom in self.symptom_disease_dict.keys():
                    if item not in self.symptom_disease_dict[symptom]:
                        self.symptom_disease_dict[symptom].append(item)
                else:
                    self.symptom_disease_dict[symptom] = [item]
                group = query.get_disease_group_iri_by_iri(disease)
                items_group = self.symptom_group_dict.setdefault(symptom, {})
                self.symptom_group_dict[symptom][group] = self.symptom_group_dict[symptom].setdefault(group, 0) + 0.8
               

            for symptom in data.probably_symptoms:
                item = {
                    "disease": disease,
                    "proportion": 0.2
                }
                if symptom in self.symptom_disease_dict.keys():
                    if item not in self.symptom_disease_dict[symptom]:
                        self.symptom_disease_dict[symptom].append(item)
                else:
                    self.symptom_disease_dict[symptom] = [item]
                group = query.get_disease_group_iri_by_iri(disease)
                items_group = self.symptom_group_dict.setdefault(symptom, {})
                self.symptom_group_dict[symptom][group] = self.symptom_group_dict[symptom].setdefault(group, 0) + 0.2
                
        self.symptom_group_dict = {k: [{'group': g, "proportion": v/len(g_item)} for g, v in g_item.items()] for k, g_item in self.symptom_group_dict.items()}
        return self.symptom_disease_dict, self.symptom_group_dict
    
    def create_nodes_and_edges(self):
        for s, _ in self.symptom_disease_dict.items():
            self.model.add_node(s)
        
        for g in self.disease_group:
            self.model.add_node(g)
        #     for symptom in d_data.symptoms + d_data.main_symptoms + d_data.probably_symptoms:
        #         self.model.add_edge(d_label, symptom)
        return self.model

    def create_symptom_cpds_table(self, symptom):
        group_data = self.symptom_group_dict[symptom]
        num_groups = len(group_data)
        
        print(num_groups)
        num_rows = np.power(2, num_groups)
        cpd_list = []
        evidence = [group_data[i]['group'] for i in range(num_groups)]
        for d in evidence:
            self.model.add_edge(d, symptom)
        evidence_card = [2]*len(evidence)
        total_proportion = sum([group_data[i]['proportion'] for i in range(num_groups)])
        for i in range(num_rows):
            total_true = 0
            cpd_state = str(bin(i)[2:].zfill(num_groups))
            # print(cpd_state)
            for state_index in range(num_groups):
                if cpd_state[state_index] == '0':
                    total_true += group_data[state_index]['proportion']
            temp_proportion = total_true/total_proportion
            cpd_list.append(temp_proportion)
        cpd_symptom = TabularCPD(symptom, 2, values=[cpd_list, [(1-x) for x in cpd_list]], evidence=evidence, evidence_card=evidence_card)
        self.model.add_cpds(cpd_symptom)
        return self.model

    def create_group_cpds_table(self, group):

        cpd_group = TabularCPD(group, 2,values=[[0.5],[0.5]]) 
        self.model.add_cpds(cpd_group)
        return self.model

    def build(self):
        self.model = BayesianModel()

        self.model = self.create_nodes_and_edges()
        for group in self.disease_group:
            self.model = self.create_group_cpds_table(group)
        
        for symptom in self.symptom_group_dict.keys():
            self.model = self.create_symptom_cpds_table(symptom)
        
        return self.model