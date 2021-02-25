import pandas as pd
import numpy as np
import pickle as pkl

import os

from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination

from pomegranate import *

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
            self.disease_field = self.query.get_diseases_by_group(disease_group)
        self.symptom_disease_dict = self.create_symptom_disease_dict()
        for filename in os.listdir(proportion_dir):
            disease_iri = 'http://deepcare.io/' + filename.split("_")[0]
            self.fill_proportion_from_files_disease(proportion_dir+filename, disease_iri)

    def create_symptom_disease_dict(self):
        self.symptom_disease_dict = {}  
        for disease, data in self.diseases.items():
            if disease not in self.disease_field:
                continue
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
        
        print(num_diseases)
        num_rows = np.power(2, num_diseases)
        cpd_list = []
        evidence = [disease_data[i]['disease'] for i in range(num_diseases)]
        if num_diseases == 17:
            print(evidence)
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

    def load_from_file(self, file_path):
        pass