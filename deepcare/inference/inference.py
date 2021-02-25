import numpy as np
import pickle as pkl
import random
import pandas as pd
import json

from deepcare.embedding.vectorize import Vectorizer
from configs import data_file

from app_symptom_checker.question_const import *

def dict_sort(x):
	dict_x_sorted = {}
	x_sorted = [(k, x[k]) for k in sorted(x, key=x.get, reverse=True)]
	for com in x_sorted:
		dict_x_sorted[com[0]] = com[1]
	return dict_x_sorted

class DC_Inference():
	def __init__(self, query, onto2vec, lang="vi"):
		# self.query = DC_Query(ontology)
		self.lang = lang
		# try:
		self.diseases = self.load_diseases(query)
		# except Exception:
		# 	self.diseases = query.get_all_diseases()
		self.diseases_name = [self.diseases[d].label for d in self.diseases.keys()]

		self.symptoms = None
		self.symptom_dict = {}
		self.symptom_dict_iri = {}
		self.compute_symptom_weights(query)
		self.symptoms_name = [self.symptoms[s].label for s in self.symptoms.keys()]
		
		self.vectorize = Vectorizer(onto2vec)
			
	def compute_symptom_weights(self, query):
		if self.lang == "vi":
			file_data = data_file.APP_SYMPTOMS_DATA_VI
			file_dict = data_file.APP_SYMPTOM_DICT_VI
		elif self.lang == "en":
			file_data = data_file.APP_SYMPTOMS_DATA_EN
			file_dict = data_file.APP_SYMPTOM_DICT_EN
			
		try:
			with open(file_data, 'rb') as handle:
				self.symptoms = pkl.load(handle)

		except Exception:
			print("computing symptom weight")
			self.symptoms = query.get_all_symptoms()
			n_disease = len(self.diseases.keys())
			count = 0
			process = -1
			total = len(self.symptoms)
			for _, symptom in self.symptoms.items():
				diseases = [d.iri for d in query.get_disease_of_symptom(symptom.label)]
				sub_symptoms = query.get_subclass_by_iri(symptom.iri)
				if sub_symptoms != 0:
					for s in sub_symptoms:
						try:
							diseases.extend([d.iri for d in query.get_disease_of_symptom(self.symptoms[s].label)])
						except Exception:
							print(s)
				diseases = list(set(diseases))
				symptoms = [s.iri for s in query.get_related_symptoms(symptom.label)]
				symptoms_where = [s.iri for s in query.get_relation_of_symptom(symptom.label, "symptom_where")]
				symptoms_when = [s.iri for s in query.get_relation_of_symptom(symptom.label, "symptom_when")]
				symptoms_how = [s.iri for s in query.get_relation_of_symptom(symptom.label, "symptom_how")]
				symptoms_gender = [s.label for s in query.get_symptom_gender(symptom.label)]
				
				if len(symptoms_gender) > 0:
					symptom.set_gender(symptoms_gender[0])

				n_symptom_disease = len(diseases)
				symptom.set_diseases(diseases)
				symptom.set_symptoms(symptoms)
				symptom.set_symptoms_where(symptoms_where)
				symptom.set_symptoms_when(symptoms_when)
				symptom.set_symptoms_how(symptoms_how)
				
				
				weight = np.power(((n_disease-n_symptom_disease)/float(n_disease-1)), 2)
				symptom.set_weight(weight)
				count += 1
				temp_process = int(count*100/total)
				if temp_process>process:
					process = temp_process
					print("{}% completed".format(process))

			print("done")
			with open(file_data, 'wb') as handle:
				pkl.dump(self.symptoms, handle)
		symptoms_label = [self.symptoms[iri].label for iri in self.symptoms.keys()]
		sym_file = open(file_dict, "w")
		for s_str in symptoms_label:
			symptoms = s_str.split(",")
			for s in symptoms:
				self.symptom_dict[s.lower().replace("_", " ")] = s_str
		for k, s in self.symptoms.items():
			symptoms = s.label.split(",")
			for s_l in symptoms:
				self.symptom_dict_iri[s_l.lower().replace("_", " ")] = k
				sym_file.write(s_l.lower() + "\n")

	def load_diseases(self, query):
		if self.lang == "vi":
			file_data = data_file.APP_DISEASES_DATA_VI
		elif self.lang == "en":
			file_data = data_file.APP_DISEASES_DATA_EN
		try:
			with open(file_data, 'rb') as handle:
				self.diseases = pkl.load(handle)

		except Exception:
			print("\n Computing diseases")
			self.diseases = query.get_all_diseases()
			count = 0
			process = -1
			total = len(self.diseases)
			for d, _ in self.diseases.items():
			# if self.diseases[d].symptoms is None:
				S_common = [s.iri for s in query.get_relation_of_disease(self.diseases[d].label, "has_symptom")]
				S_main = [s.iri for s in query.get_relation_of_disease(self.diseases[d].label, "has_main_symptom")]
				S_uncommon = [s.iri for s in query.get_relation_of_disease(self.diseases[d].label, "probably_has_symptom")]
				S_serious = [s.iri for s in query.get_relation_of_disease(self.diseases[d].label, "serious_symptom")]
				age = [s.label for s in query.get_relation_of_disease(self.diseases[d].label, "age")]
				gender_common = [s.label for s in query.get_relation_of_disease(self.diseases[d].label, "common_gender")]
				gender_only = [s.label for s in query.get_relation_of_disease(self.diseases[d].label, "only_in_gender")]
				causes = [s.label for s in query.get_relation_of_disease(self.diseases[d].label, "can_be_caused_by")]
				# label_en = query.get_see_also_by_iri(self.diseases[d].iri)

				S_common = list(set(S_common) - set(S_main))
				S_uncommon = list(set(S_uncommon) - set(S_main) - set(S_common))

				self.diseases[d].set_symptoms(S_common)
				self.diseases[d].set_main_symptoms(S_main)
				self.diseases[d].set_probably_symptoms(S_uncommon)
				self.diseases[d].set_serious_symptoms(S_serious)
				self.diseases[d].set_age(age)
				self.diseases[d].set_gender_common(gender_common)
				self.diseases[d].set_gender_only(gender_only)
				self.diseases[d].set_causes(causes)
				count += 1
				temp_process = int(count*100/total)
				if temp_process>process:
					process = temp_process
					print("{}% completed".format(process))

			print("done")
			with open(file_data, 'wb') as handle:
				pkl.dump(self.diseases, handle)

		return self.diseases

	def compute_disease_proportion(self, disease, positive_user_symptoms, negative_user_symptoms, query):
		S_common = self.diseases[disease].symptoms
		S_main = self.diseases[disease].main_symptoms
		S_uncommon = self.diseases[disease].probably_symptoms

		for s in negative_user_symptoms:
			if s in S_main:
				return 0

		##find some small sets
		user_main_symptoms = list(set(S_main)&set(positive_user_symptoms))
		
		user_common_symptoms_positive = list(set(S_common)&set(positive_user_symptoms))
		user_common_symptoms_negative = list(set(S_common)&set(negative_user_symptoms))
		
		user_uncommon_symptoms = list(set(S_uncommon)&set(positive_user_symptoms))

		# user_other_symptoms = list(set(positive_user_symptoms)-set(user_uncommon_symptoms))

		#compute score for each sets
		positive_main_score = np.sum([self.symptoms[s].weight for s in user_main_symptoms])
		positive_common_score = np.sum([self.symptoms[s].weight for s in user_common_symptoms_positive])
		positive_uncommon_score = np.sum([self.symptoms[s].weight for s in user_uncommon_symptoms])

		negative_common_score = np.sum([self.symptoms[s].weight for s in user_common_symptoms_negative])

		disease_weight = np.sum([self.symptoms[s].weight for s in S_main + S_common])

		#compute total score
		score = (30*positive_main_score + 15*positive_common_score + 5*positive_uncommon_score - 5*negative_common_score)/(50.0)
		if score <= 0:
			return 0
		else:
			return score*100/disease_weight
	
	def score_disease_by_symptom(self, disease, positive_user_symptoms, negative_user_symptoms, query):	
		S_common = self.diseases[disease].symptoms
		S_main = self.diseases[disease].main_symptoms
		S_uncommon = self.diseases[disease].probably_symptoms

		for s in negative_user_symptoms:
			if s in S_main:
				return 0

		##find some small sets
		user_main_symptoms = list(set(S_main)&set(positive_user_symptoms))
		
		user_common_symptoms_positive = list(set(S_common)&set(positive_user_symptoms))
		user_common_symptoms_negative = list(set(S_common)&set(negative_user_symptoms))
		
		user_uncommon_symptoms = list(set(S_uncommon)&set(positive_user_symptoms))

		# user_other_symptoms = list(set(positive_user_symptoms)-set(user_uncommon_symptoms))

		#compute score for each sets
		positive_main_score = np.sum([self.symptoms[s].weight for s in user_main_symptoms])
		positive_common_score = np.sum([self.symptoms[s].weight for s in user_common_symptoms_positive])
		positive_uncommon_score = np.sum([self.symptoms[s].weight for s in user_uncommon_symptoms])

		negative_common_score = np.sum([self.symptoms[s].weight for s in user_common_symptoms_negative])

		disease_weight = np.sum([self.symptoms[s].weight for s in S_main + S_common])/float(len(S_main + S_common))

		#compute total score
		score = (30*positive_main_score + 15*positive_common_score + 5*positive_uncommon_score - 15*negative_common_score)/(50.0*(len(positive_user_symptoms)))
		if score <= 0:
			return -1
		else:
			return score/disease_weight

	def score_disease_by_causes(self, disease, positive_user_causes, negative_user_causes):
		if len(positive_user_causes) == 0:
			return 1
		C = self.diseases[disease].causes
		X = list(set(C)&set(negative_user_causes))
		user_causes = list(set(C)&set(positive_user_causes))
		if len(X) > len(C)/2:
			return 1/(1+len(X)) + len(user_causes)/float(len(positive_user_causes))
		return 1 + len(user_causes)/float(len(positive_user_causes))

	def score_disease(self, disease, positive_user_symptoms, negative_user_symptoms, age, gender, positive_user_causes, negative_user_causes, query):
		
		if age in self.diseases[disease].age:
			w_age = 1.0
		elif len(self.diseases[disease].age) == 0:
			w_age = 0.8
		else:
			w_age = 0.4

		if len(self.diseases[disease].gender_only) == 0:
			if gender in self.diseases[disease].gender_common:
				w_gender = 1.0
			elif len(self.diseases[disease].gender_common) == 0:
				w_gender = 0.8
			else:
				w_gender = 0.6
		else:
			if gender in self.diseases[disease].gender_only:
				w_gender = 1.0
			else:
				w_gender = 0
		
		w_symptom = self.score_disease_by_symptom(disease, positive_user_symptoms, negative_user_symptoms, query)
		w_cause = self.score_disease_by_causes(disease, positive_user_causes, negative_user_causes)

		return w_age*w_gender*w_symptom*w_cause

	def score_diseases(self, diseases, positive_user_symptoms, negative_user_symptoms, age, gender, positive_user_causes, negative_user_causes, query):
		diseases_score = {}
		for d in diseases:
			score = self.score_disease(d, positive_user_symptoms, negative_user_symptoms, age, gender, positive_user_causes, negative_user_causes, query)
			if score>0:
				diseases_score[d] = score
			elif score <= 0:
				diseases_score[d] = 0
		ranked_diseases = dict_sort(diseases_score)
		return ranked_diseases

	def get_next_symptoms(self, diseases_score, symptoms, positive_user_symptoms, negative_user_symptoms, age, gender, positive_user_causes, negative_user_causes, q_count, query):
		diseases = list(diseases_score.keys())
		top_disease = list(diseases_score.keys())[0]
		top_score = self.get_disease_probability(top_disease, positive_user_symptoms) - self.get_disease_probability(top_disease, negative_user_symptoms)
		symptoms_to_consider = list(set(symptoms) - set(positive_user_symptoms) - set(negative_user_symptoms))
		# print("SymToCon")
		# for s in symptoms_to_consider:
		# 	print(self.symptoms[s].label)
		symptoms_score = dict.fromkeys(symptoms_to_consider, 0)
		for s in symptoms_to_consider:
			temp_positive_user_symptoms = positive_user_symptoms + [s]
			temp_diseases_score = self.score_diseases(diseases, temp_positive_user_symptoms, negative_user_symptoms, age, gender, positive_user_causes, negative_user_causes, query)
			temp_top_disease = list(temp_diseases_score.keys())[0]
			temp_top_score = self.get_disease_probability(temp_top_disease, temp_positive_user_symptoms) - self.get_disease_probability(temp_top_disease, negative_user_symptoms)
			
			if temp_top_score < 0.6 or temp_top_score <= top_score:
				different_dict = [(temp_diseases_score[d] - diseases_score[d]) for d in temp_diseases_score.keys()]
				w_disease = np.sum(different_dict) + np.sum(np.absolute(different_dict))
				if s in self.symptoms[positive_user_symptoms[0]].related_symptoms:
					w_s = 1 + (self.vectorize.similarity(s, positive_user_symptoms[0]))/float(q_count)
				else:
					w_s = 1.0
				symptom_score = w_s*w_disease
			else:
				symptom_score = 1000000*temp_top_score
			symptoms_score[s] = np.absolute(symptom_score)
		ranked_symptoms_score = dict_sort(symptoms_score)
		# print(ranked_symptoms_score)
		return ranked_symptoms_score

	def get_related_diseases(self, symptom):
		# print([self.diseases[d].label for d in self.symptoms[symptom].related_diseases])
		return self.symptoms[symptom].related_diseases

	def get_related_symptoms(self, diseases, query):
		if self.lang == "vi":
			file_data = data_file.APP_DISEASES_DATA_VI
		elif self.lang == "en":
			file_data = data_file.APP_DISEASES_DATA_EN
		related_symptoms = []
		for d in diseases:
			if self.diseases[d].symptoms is None:
				S_common = [s.iri for s in query.get_relation_of_disease(self.diseases[d].label, "has_symptom")]
				S_main = [s.iri for s in query.get_relation_of_disease(self.diseases[d].label, "has_main_symptom")]
				S_uncommon = [s.iri for s in query.get_relation_of_disease(self.diseases[d].label, "probably_has_symptom")]
				S_serious = [s.iri for s in query.get_relation_of_disease(self.diseases[d].label, "serious_symptom")]
				age = [s.label for s in query.get_relation_of_disease(self.diseases[d].label, "age")]
				gender_common = [s.label for s in query.get_relation_of_disease(self.diseases[d].label, "common_gender")]
				gender_only = [s.label for s in query.get_relation_of_disease(self.diseases[d].label, "only_in_gender")]
				causes = [s.label for s in query.get_relation_of_disease(self.diseases[d].label, "can_be_caused_by")]
				# label_en = query.get_see_also_by_iri(self.diseases[d].iri)

				S_common = list(set(S_common) - set(S_main))
				S_uncommon = list(set(S_uncommon) - set(S_main) - set(S_common))

				self.diseases[d].set_symptoms(S_common)
				self.diseases[d].set_main_symptoms(S_main)
				self.diseases[d].set_probably_symptoms(S_uncommon)
				self.diseases[d].set_serious_symptoms(S_serious)
				self.diseases[d].set_age(age)
				self.diseases[d].set_gender_common(gender_common)
				self.diseases[d].set_gender_only(gender_only)
				self.diseases[d].set_causes(causes)
				# self.diseases[d].set_label_en(label_en)

			related_symptoms.extend(self.diseases[d].symptoms + self.diseases[d].main_symptoms + self.diseases[d].probably_symptoms)
		with open(file_data, 'wb') as handle:
			pkl.dump(self.diseases, handle)
		return list(set(related_symptoms))

	def get_disease_probability(self, disease, positive_user_symptoms):
		S_common = self.diseases[disease].symptoms
		S_main = self.diseases[disease].main_symptoms
		S_uncommon = self.diseases[disease].probably_symptoms

		user_main_symptoms = list(set(S_main)&set(positive_user_symptoms))
		user_common_symptoms = list(set(S_common)&set(positive_user_symptoms))
		user_uncommon_symptoms = list(set(S_uncommon)&set(positive_user_symptoms))

		main_score = np.sum([self.symptoms[s].weight for s in S_main])
		common_score = np.sum([self.symptoms[s].weight for s in S_common])
		uncommon_score = np.sum([self.symptoms[s].weight for s in S_uncommon])

		user_main_score = np.sum([self.symptoms[s].weight for s in user_main_symptoms])
		user_common_score = np.sum([self.symptoms[s].weight for s in user_common_symptoms])
		user_uncommon_score = np.sum([self.symptoms[s].weight for s in user_uncommon_symptoms])

		return (3.5*user_main_score + 1.5*user_common_score + 0.5*user_uncommon_score)/(3.5*main_score + 1.5*common_score + 0.5*uncommon_score)
	
	def get_symptom(self, query):
		symptom_labels = [self.symptoms[x].label for x in self.symptoms.keys()]
		while True:
			ans = input("\nHãy nhập gì đó: ")
			if ans in symptom_labels:
				print(ans)
				return ans
			else:
				output_list = query.get_position_subclass_by_label(ans)
				if output_list != 0:
					print(output_list)
				else:
					output_list = query.get_symptoms_by_position(ans)
					if output_list != 0:
						print(output_list)
		return ""
	
	def get_info_by_string(self, string_input:str, query):
		# symptom_labels = [self.symptoms[x].label for x in self.symptoms.keys()]
		symptom_labels = list(self.symptom_dict.keys())
		if string_input in symptom_labels:
			return self.symptom_dict[string_input], "symptom_init"
		else:
			output_list = query.get_position_subclass_by_label(string_input)
			if output_list != 0:
				return output_list, "sub_positions_list"
			else:
				output_list = query.get_symptoms_by_position(string_input)
				if output_list != 0:
					return output_list, "symptoms_list"
		return [], "unknown"
		

class DC_SymptomChecker():
	def __init__(self, user, symptom_init, inference, query):
		self.user = user
		self.symptom_init = symptom_init
		self.inference = inference
		self.lang = inference.lang
		self.question_answer = []
		# print(str(self.question_answer))
		self.diseases_init = self.inference.get_related_diseases(symptom_init)
		
		self.symptoms_init = self.inference.get_related_symptoms(self.diseases_init, query)
		self.symptoms_init = list(set(self.symptoms_init) - set([symptom_init]))
		
		self.faculty_list = pd.read_csv(data_file.APP_FACULTY)
		self.faculty_group = pd.read_csv(data_file.APP_FACULTY_GROUP)

		symptom_filter_gender = []
		for s in self.symptoms_init:
			if inference.symptoms[s].gender == None or inference.symptoms[s].gender == user.gender:
				symptom_filter_gender.append(s)
		self.symptoms_init = symptom_filter_gender

		self.related_symptoms = self.inference.symptoms[symptom_init].related_symptoms
		
		self.answer_tracking = []
		self.disease_tracking = []
		self.same_disease_count = 1

		self.prev_answer = "idk"

		self.positive_user_symptoms = [symptom_init]

		p_symptom_init = query.get_parent_symptoms_by_iri(symptom_init)
		if p_symptom_init != 0:
			self.positive_user_symptoms.extend([s[1] for s in p_symptom_init])

		self.negative_user_symptoms = []

		# self.ask_init()

		self.positive_user_causes = []
		self.negative_user_causes = []

		self.diseases_score = self.inference.score_diseases(self.diseases_init, self.positive_user_symptoms, self.negative_user_symptoms, user.age, user.gender, self.positive_user_causes, self.negative_user_causes, query)
		# try:
		self.disease_tracking.append(list(self.diseases_score.keys())[0])
		self.symptoms_to_ask = self.inference.get_next_symptoms(self.diseases_score, self.symptoms_init, self.positive_user_symptoms, self.negative_user_symptoms, user.age, user.gender, self.positive_user_causes, self.negative_user_causes, len(self.answer_tracking), query)
		# except Exception:
		# 	self.symptoms_to_ask = None
		self.can_stop = False

	def update_question_answer(self, question, answer):
		data = {"question" : question, "answer" : answer}
		self.question_answer.append(data)

	def get_init_questions(self):
		symptoms_where = self.inference.symptoms[self.symptom_init].symptoms_where
		symptoms_when = self.inference.symptoms[self.symptom_init].symptoms_when
		symptoms_how = self.inference.symptoms[self.symptom_init].symptoms_how
		data = {
			"where" : {
				"iri" : symptoms_where,
				"label" : [self.inference.symptoms[s].label for s in symptoms_where]
			},
			"when" : {
				"iri" : symptoms_when,
				"label" : [self.inference.symptoms[s].label for s in symptoms_when]
			},
			"how" : {
				"iri" : symptoms_how,
				"label" : [self.inference.symptoms[s].label for s in symptoms_how]
			}
		}
		return data

	def ask_cause(self, disease):
		causes = self.inference.diseases[disease].causes
		num_causes = len(list(set(self.positive_user_causes)&set(causes)))
		if num_causes >= min(3, len(causes)) and len(causes)>=2:
			return "stop", "stop"
		else:
			causes = list(set(causes)-set(self.positive_user_causes)-set(self.negative_user_causes))
			disease_causes = list(set(causes)&set(self.inference.diseases_name))
		if "Di_truyền" in causes:
			question = "Có ai trong gia đình bạn bị %s không ?" % (self.inference.diseases[disease].label)
			return question, "Di_truyền"
		elif "Lây_nhiễm" in causes:
			question = "Bạn có đến những nơi có dịch %s hay tiếp xúc với ai nhiễm không ?" % (self.inference.diseases[disease].label)
			return question, "Lây_nhiễm"
		elif len(disease_causes) > 0:
			disease_cause = random.choice(disease_causes)
			question = "Bạn có bị %s không ?" % (disease_cause)
			return question, disease_cause
		else:
			num_sample = min(len(causes), 3)
			if num_sample == 0:
				return 0, 0
			elif num_sample == 1:
				question = "Bạn có hành vi sau đây ko? %s" % (causes[0])
				return question, causes[0]
			else:
				return causes, causes

	def compute_disease_level_of_serious(self, disease, progress, time, level):
		S_main = self.inference.diseases[disease].main_symptoms
		S_common = self.inference.diseases[disease].symptoms
		S_uncommon = self.inference.diseases[disease].probably_symptoms

		S = list(set(S_main + S_common + S_uncommon))
		user_positive_S = list(set(S) & set(self.positive_user_symptoms))

		serious_symptoms = self.inference.diseases[disease].serious_symptoms
		user_serious_S = list(set(serious_symptoms) & set(self.positive_user_symptoms))
		
		symptoms_score = len(user_positive_S)/len(S)
		serious_score = len(user_serious_S)

		total_score = level/time + symptoms_score + serious_score + np.sqrt(progress*time) + level

		return total_score

	def check_stop(self):
		if len(self.diseases_score) == 0:
			print("diseases_score")
			return 1
		if self.same_disease_count == 8:
			print("same_disease_count")
			return 1
		if len(self.symptoms_to_ask) == 0:
			print("symptoms_to_ask")
			return 1
		if len(set(self.positive_user_symptoms)) > 15:
			print("positive_user_symptoms")
			return 1
		if len(self.disease_tracking) > 10:
			print("num_questions_limit")
			return 1
		return 0

	def compute_severity(self, disease, serious_symptom_D, serious_symptom_S, time, level, progress):
		S_main = self.inference.diseases[disease].main_symptoms
		S_common = self.inference.diseases[disease].symptoms
		S_uncommon = self.inference.diseases[disease].probably_symptoms

		time_score = SYMPTOM_TIME[time]
		level_score = int(level)
		progress_score = SYMPTOM_PROGRESS[progress]

		S = list(set(S_main + S_common + S_uncommon))
		user_positive_S = list(set(S) & set(self.positive_user_symptoms))

		serious_symptoms = self.inference.diseases[disease].serious_symptoms
		user_serious_S = list(set(serious_symptoms) & set(self.positive_user_symptoms))
		
		symptoms_score = len(user_positive_S)/len(S)
		serious_score = len(user_serious_S)

		total_score = level_score/time_score + symptoms_score + serious_score + np.sqrt(progress_score*time_score) + level_score + len(serious_symptom_D + serious_symptom_S)

		return total_score

	def get_multiple_choice_question(self):
		if self.check_stop():
			return {"result" : "stop"}
		if self.same_disease_count % 4 == 0 and self.lang == "vi":
		# if 0 == 1:
			question, causes = self.ask_cause(list(self.diseases_score.keys())[0])
			if question != 0:
				if isinstance(question, str):
					if question == "stop":
						return {"result" : "stop"}
					data = {
						"type" : "cause",
						"a_type": "single",
						"question" : question.replace("_", " "),
						"answer" : [causes],
						"items" : {
							"label" : ANSWER_SINGLE[self.lang],
							"iri" : ["yes", "no"]
						}
					}
					return data
				else:
					data = {
						"type" : "causes_list",
						"a_type": "multiple",
						"question" : QUESTION_CAUSE[self.lang]["multiple"],
						"answer" : [q.split(",")[0].replace("_", " ") for q in question],
						"items" : {
							"label" : [q.split(",")[0].replace("_", " ") for q in question],
							"iri" : question
						}
					}
					return data
		top_symptoms_list = list(self.symptoms_to_ask.keys())[:20]
		top_disease = list(self.diseases_score.keys())[0]
		top_disease_symptom = self.inference.diseases[top_disease].symptoms + self.inference.diseases[top_disease].main_symptoms + self.inference.diseases[top_disease].probably_symptoms
		symptoms_to_ask_list = []

		for s in top_symptoms_list:
			if s in top_disease_symptom:
				symptoms_to_ask_list.append(s)
		if len(symptoms_to_ask_list)>=3:
			data = {
				"type" : "symptoms_list",
				"a_type": "multiple",
				"question" : QUESTION_SYMPTOM[self.lang]["multiple"],
				"answer" : [self.inference.symptoms[s].label.split(",")[0].replace("_", " ") for s in symptoms_to_ask_list[0:4]],
				"items" : {
					"label" : [self.inference.symptoms[s].label.split(",")[0].replace("_", " ") for s in symptoms_to_ask_list[0:4]],
					"iri" : symptoms_to_ask_list[0:4]
				}
			}
			return data
		elif len(symptoms_to_ask_list) < 3 :
			next_symptoms_list = list(self.symptoms_to_ask.keys())[0:4]
			data = {
				"type" : "symptoms_list",
				"a_type": "multiple",
				"question" : QUESTION_SYMPTOM[self.lang]["multiple"],
				"answer" : [self.inference.symptoms[s].label.split(",")[0].replace("_", " ") for s in next_symptoms_list],
				"items" : {
					"label" : [self.inference.symptoms[s].label.split(",")[0].replace("_", " ") for s in next_symptoms_list],
					"iri": next_symptoms_list
				}
			}
			return data
		else:
			next_symptom = list(self.symptoms_to_ask.keys()).pop(0)
			self.symptoms_init = list(set(self.symptoms_init) - set([next_symptom]))
			data = {
				"type" : "symptom",
				"a_type": "single",
				"question" : QUESTION_SYMPTOM[self.lang]["single"]%(self.inference.symptoms[next_symptom].label.split(",")[0].replace("_", " ")),
				"answer" : next_symptom,
				"items" : {
					"label" : ["Có", "Không"],
					"iri" : ["yes", "no"]
				}
			}
			return data

	def get_symptom_to_ask_for_severity(self):
		diseases = list(self.diseases_score.keys())[0:4]
		serious_symptoms = []
		for d in diseases:
			serious_symptoms.extend(self.inference.diseases[d].serious_symptoms)
		serious_symptoms = list(set(serious_symptoms) - set(self.positive_user_symptoms) - set(self.negative_user_symptoms))

		serious_symptoms_S = list(set(serious_symptoms) & set(list(self.inference.symptoms.keys())))
		serious_symptoms_D = list(set(serious_symptoms) & set(list(self.inference.diseases.keys())))
		data = {
			"diseases": {
				"label": [self.inference.diseases[d].label.split(",")[0].replace("_", " ") for d in serious_symptoms_D],
				"iri": serious_symptoms_D,
			},
			"symptoms": {
				"label": [self.inference.symptoms[s].label.split(",")[0].replace("_", " ") for s in serious_symptoms_S],
				"iri": serious_symptoms_S
			} 
		}
		if len(data["diseases"]["iri"]) == 0:
			data["diseases"]["question"] = ""
			data["diseases"]["answers"] = ""
			data['diseases']['a_type'] = ""
		elif len(data["diseases"]["iri"]) == 1:
			data["diseases"]["question"] = QUESTION_DISEASE[self.lang]["single"]%(data["diseases"]["label"][0])
			data["diseases"]["label"] = ANSWER_SINGLE[self.lang]
			data["diseases"]["answers"] = ["yes", "no"]
			data["diseases"]["iri"] = ["yes", "no"]
			data['diseases']['a_type'] = "single"
		else:
			data["diseases"]["question"] = QUESTION_DISEASE[self.lang]["multiple"]
			data["diseases"]["answers"] = data["diseases"]["label"]
			data['diseases']['a_type'] = "multiple"

		if len(data["symptoms"]["iri"]) == 0:
			data["symptoms"]["question"] = ""
			data["symptoms"]["answers"] = ""
			data['symptoms']['a_type'] = ""
		elif len(data["symptoms"]["iri"]) == 1:
			data["symptoms"]["question"] = QUESTION_SYMPTOM[self.lang]["single"]%(data["symptoms"]["label"][0])
			data["symptoms"]["label"] = ANSWER_SINGLE[self.lang]
			data["symptoms"]["answers"] = ["yes", "no"]
			data["symptoms"]["iri"] = ["yes", "no"]
			data['symptoms']['a_type'] = "single"
		else:
			data["symptoms"]["question"] = QUESTION_SYMPTOM[self.lang]["multiple"]
			data["symptoms"]["answers"] = data["symptoms"]["label"]
			data['symptoms']['a_type'] = "multiple"

		return data
	
	def update_checker(self, positive_symptoms, negative_symptoms, query):
		# print("update checker")
		# print("Pos")
		# for s in self.positive_user_symptoms:
		# 	print(self.inference.symptoms[s].label)
		# print("Neg")
		# for s in self.negative_user_symptoms:
		# 	print(self.inference.symptoms[s].label)
		
		# print(self.symptoms_init)
		self.positive_user_symptoms.extend(positive_symptoms)
		for s in negative_symptoms:
			sub = query.get_instance_subclass_by_iri(s)
			self.negative_user_symptoms.append(s)
			self.negative_user_symptoms.extend(sub)
			self.symptoms_init = list(set(self.symptoms_init) - set(sub))
		self.diseases_score = self.inference.score_diseases(list(self.diseases_score.keys()), self.positive_user_symptoms, self.negative_user_symptoms, self.user.age, self.user.gender, self.positive_user_causes, self.negative_user_causes, query)
		if list(self.diseases_score.keys())[0] == self.disease_tracking[-1]:
			self.same_disease_count += 1
		else:
			self.same_disease_count = 1
		self.disease_tracking.append(list(self.diseases_score.keys())[0])
		self.symptoms_to_ask = self.inference.get_next_symptoms(self.diseases_score, self.symptoms_init, self.positive_user_symptoms, self.negative_user_symptoms, self.user.age, self.user.gender, self.positive_user_causes, self.negative_user_causes, len(self.answer_tracking), query)
	
	def get_serverity_level(self,serve_score):
		if serve_score < 5:
			return 1
		elif serve_score >= 5 and serve_score < 8:
			return 2
		else:
			return 3


	def get_final_result(self, serious_symptom_D, serious_symptom_S, time, level, progress, query):
		data = []
		top_diseases = list(self.diseases_score.keys())[0:4]
		for d in top_diseases:
			serve_score = self.compute_severity(d, serious_symptom_D, serious_symptom_S, time, level, progress)
			faculty = query.get_disease_group_by_iri(d)
			flag =  query.get_disease_flag_by_iri(d)
			try:
				icd10 = query.get_icd10_by_iri(d)
			except Exception:
				icd10 = ""
			disease = {
				"label": self.inference.diseases[d].label,
				"iri": d,
				"ranking_score": self.diseases_score[d],
				"disease_score": self.inference.compute_disease_proportion(d, self.positive_user_symptoms, self.negative_user_symptoms, query),
				"severity_score": serve_score,
				"level": self.get_serverity_level(serve_score),
				"recommend": RECOMMEND[self.get_serverity_level(serve_score)],
				"faculty_name": faculty,
				"icd10": icd10,
				"flag": flag
				# "faculty_code": ['none' if len(self.get_faculty(icd10, group))>0 else self.get_faculty(icd10, group)[0]],
				# "faculty_name": ['none' if len(self.get_faculty(icd10, group, properties="Faculty_name"))>0 else self.get_faculty(icd10, group, properties="Faculty_name")[0]]
			}
			try:
				lab_test = [s.label for s in query.get_relation_of_disease(self.inference.diseases[d].label, "lab_test")]
				disease["lab_test"] = lab_test
			except Exception:
				pass
			data.append(disease)
		return data
	
	# def filt(self, query):
	# 	res = []
	# 	for d in self.inference.diseases:
	# 		iri = d
	# 		label = self.inference.diseases[d].label
	# 		group = query.get_disease_group_by_iri(d)
	# 		try:
	# 			icd10 = query.get_icd10_by_iri(d)
	# 		except Exception:
	# 			icd10 = ""
	# 		group = query.get_disease_group_by_iri(d)
			
	# 		fal = self.get_faculty(icd10, group)
	# 		if len(fal) == 0:
	# 			data = {"icd10" : icd10,
	# 					"iri" : iri,
	# 					"label" : label,
	# 					"group" : group}
	# 			res.append(data)
	# 	f = open("lack.json", "w", encoding='utf-8')
	# 	json.dump(res, f, indent=4, ensure_ascii=False)
	# 	return res
	
	def get_faculty(self, icd10, group, properties="Faculty_code"):
		icd10 = icd10.replace("*","").replace("†","")
		icd_split = icd10.split(".")
		icd_list = [icd10]
		result = []
		if len(icd_split) > 1 and icd10[-1] == "0":
			icd_list.append(icd_split[0])
		if len(icd_list) == 1:
			icd_list.append(icd10 + ".0")
		for icd in icd_list:
			indexes = self.faculty_list.index[self.faculty_list['ICD10']==icd].tolist()
			if len(indexes) > 0:
				for i in indexes:
					result.append(self.faculty_list.iloc[i][properties])
		if len(result) == 0:
			indexes = self.faculty_group.index[self.faculty_group['group_onto']==group]
			if len(indexes) > 0:
				for i in indexes:
					result.append(self.faculty_group.iloc[i][properties])
		return result
