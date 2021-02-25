import numpy as np
import pickle as pkl
import pandas as pd
import random

from configs import data_file

from pgmpy.readwrite import BIFReader
from pgmpy.inference import VariableElimination
from pgmpy.factors.discrete import TabularCPD, State

from pgmpy.sampling import BayesianModelSampling
from deepcare.bayesian_network.model import *
from app_symptom_checker.question_const import *

def dict_sort(x):
	dict_x_sorted = {}
	x_sorted = [(k, x[k]) for k in sorted(x, key=x.get, reverse=True)]
	for com in x_sorted:
		dict_x_sorted[com[0]] = com[1]
	return dict_x_sorted

class DC_Model_Inference():
	
	def __init_(self):
		
		self.common_symptoms = []
		self.symptom_group_dict = []
		self.symptom_disease_dict = []
		pass

	def get_suitable_models_from_symptom(self, symptom, query):
		if symptom in self.common_symptoms:
			bayes = DC_Bayesian_General_Network(query)
			bayes.build()
			return [bayes], True
		else:
			bayes = []
			for disease_group in self.symptom_group_dict[symptom][:4]:
				b = DC_Bayesian_Network(query, disease_group=disease_group, proportion_dir=data_file.APP_PROPORTION_DIR)
				b.build()
				bayes.append(b)
			return bayes, False
	
	def get_top_nodes_from(self, models, observe, size=1000, num=4, fields=[], age=0, gender=0):
		top_list = []
		top_dict = {}
		for model in models:
			bayes_network = model.model
			positive_symptoms = observe['symptoms']['positive']
			negative_symptoms = observe['symptoms']['negative']

			symptom_group_dict = model.symptom_group_dict
			symptom_field = [s for s in symptom_group_dict]

			positive_symptoms_in_field = list(set(positive_symptoms)&set(symptom_field))
			negative_symptoms_in_field = list(set(negative_symptoms)&set(symptom_field))

			conditions = [] 
			for s in positive_symptoms_in_field:
				conditions.append(State(s, 1))
			for s in negative_symptoms_in_field:
				conditions.append(State(s, 0))
			top_list.extend(self.get_top_nodes(bayes_network, conditions=conditions))
		
		for item in top_list:
			top_dict[item[0]] = top_dict.setdefault(item[0], 0) + item[1]
		top_dict = {v: np.sum(top_dict[v].tolist()) for v in top_dict}
		top_nodes = [(k,v) for k, v in sorted(top_dict.items(), key=lambda item: item[1], reverse=True) if k in fields]
		return top_nodes[:num]
	
	
		
			

	def get_top_nodes(self, model, conditions=[], size=1000, num=4, fields=[]):
		sampler = BayesianModelSampling(model)
		samples = sampler.rejection_sample(evidence=conditions, size=size)
		
		top_symp = {v: np.sum(samples[v].tolist()) for v in samples}
		top_symp = [(k,v) for k, v in sorted(top_symp.items(), key=lambda item: item[1], reverse=True) if k in fields]
		return top_symp[0:num]

# class Symptom_Checker():
# 	def __init__(self, symptom_init, positive_user_symptoms=[], negative_user_symptoms=[]):
		
# 		self.positive_user_symptoms = positive_user_symptoms
# 		self.negative_user_symptoms = negative_user_symptoms
# 		self.symptom_init = symtom_init
		
# 		pass

# 	def get_init_questions(self):
# 		pass