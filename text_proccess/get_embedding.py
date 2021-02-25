import gensim
import numpy as np
import pickle as pkl

f = open("/home/trith/Work/DeepCare/lab/Symptom_Checker/data/symptoms.txt")
symptoms = f.readlines()
symptoms = [s.replace("_", " ") for s in symptoms]

# embeddings_index = {}
# f = open("/home/trith/Work/DeepCare/lab/Symptom_Checker/data/vec_model/cc.vi.300.vec")
# dic = open("/home/trith/Work/DeepCare/lab/Symptom_Checker/data/vec_model/dic.txt", "w")
# for line in f:
#     values = line.split()
#     word = values[0]
#     dic.write(word + "\n")
#     if word in symptoms:
#         coefs = np.asarray(values[1:], dtype='float32')
#         embeddings_index[word] = coefs

# with open("/home/trith/Work/DeepCare/lab/Symptom_Checker/data/vec_model/symp_vec.pkl", "wb") as handle:
#     pkl.dump(embeddings_index, handle)

# with open("/home/trith/Work/DeepCare/lab/Symptom_Checker/data/vec_model/symp_vec.pkl", 'rb') as handle:
# 	symptoms = pkl.load(handle)

# print(symptoms.keys())

# model = gensim.models.KeyedVectors.load_word2vec_format("/home/trith/Work/DeepCare/lab/Symptom_Checker/data/vec_model/wiki.vi.model.bin", binary=True)
# model.wv.save_word2vec_format('/home/trith/Work/DeepCare/lab/Symptom_Checker/data/vec_model/cbow_model.txt',binary=False)

# from gensim.models import word2vec

# model = word2vec.Word2Vec.load_word2vec_format("/home/trith/Work/DeepCare/lab/Symptom_Checker/data/vec_model/wiki.vi.model.bin", binary=True)

# model.save_word2vec_format('/home/trith/Work/DeepCare/lab/Symptom_Checker/data/vec_model/cbow_model.txt', binary=False)

