import numpy as np
import pandas as pd
import pickle as pkl
import setting

from sklearn.metrics.pairwise import cosine_similarity
from configs import data_file

class Vectorizer:
    def __init__(self, onto2vec_path:str):
        self.onto2vec = onto2vec_path
        self.words, self.word_vectors = self.read_iri_vecs()
        # self.sim = np.load(sim_path)
        # d = pd.read_csv('/home/trith/Work/DeepCare/symptomCheckerVN/Dictionary.csv')
        # self.dic = {}
        # for i in d.index:
        #     self.dic[d.Key.loc[i]] = d.Values.loc[i]
        # self.compute_similarity_matrix()
        try:
            self.similarity_matrix = pkl.load(open(data_file.APP_SIMILARITY_DATA, "rb"))
        except Exception:
            self.similarity_matrix = self.compute_similarity_matrix()    
    
    def iri_to_vec(self, iri:str):
        return self.word_vectors[iri]
    
    def read_iri_vecs(self):
        with open(self.onto2vec, 'r') as f:
            words = set()
            word_to_vec_map = {}
            for line in f:
                line = line.strip().split()
                word = line[0]
                words.add(word)
                word_to_vec_map[word] = np.array(line[1:], dtype=np.float64)
        return words, word_to_vec_map
    
    def compute_similarity_matrix(self):
        print("computing matrix")
        sim_dict = {}
        for word_1 in self.words:
            word_1_iri = "<" + word_1 +">"
            sim_dict[word_1_iri] = {}
            vec_1 = self.word_vectors[word_1]
            for word_2 in self.words:
                word_2_iri = "<" + word_2 +">"
                vec_2 = self.word_vectors[word_2]
                sim = cosine_similarity([vec_1], [vec_2])
                sim_dict[word_1_iri][word_2_iri] = sim[0][0]
        print("save matrix")
        f = open(data_file.APP_SIMILARITY_DATA, "wb")
        pkl.dump(sim_dict, f)
        f.close()
        return sim_dict

    def similarity(self, iri_1:str, iri_2:str):
        try:
            # vec_1 = [self.word_vectors[cui] for cui in cui_1]
            # vec_2 = [self.word_vectors[cui] for cui in [cui_2]]
            # sim = cosine_similarity(vec_1, vec_2)[0]
            # return np.average(sim)
            return self.similarity_matrix[iri_1][iri_2]
        except Exception:
            return -2
