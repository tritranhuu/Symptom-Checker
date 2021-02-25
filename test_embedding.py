# # from deepcare.embedding.vectorize import Vectorizer

# import pandas as pd

# # if __name__ == "__main__":
#     # vec = Vectorizer("./embedding/onto2vec.bin")
#     # print(vec.similarity("<http://deepcare.io/faa969f2_f088_4748_b782_2100031e30b4>","<http://deepcare.io/RBGiYCglj18H7Ys8baZojlM>"))
#     # print(vec.similarity("<http://deepcare.io/7a882d75_4feb_442a_84c3_22d94bf93772>","<http://deepcare.io/913e9bb3_1198_4480_a906_08bbfe9b2522>"))
# def get_faculty(icd10):
#     faculty_list = pd.read_csv('./data/dictionary/faculty_list.csv')
#     icd10 = icd10.replace("*","").replace("†","")
#     icd_split = icd10.split(".")
#     icd_list = [icd10]
#     result = []
#     if len(icd_split) > 1 and icd10[-1] == "0":
#     	icd_list.append(icd_split[0])
#     if len(icd_list) == 1:
#     	icd_list.append(icd10 + ".0")
#     for icd in icd_list:
#     	indexes = faculty_list.index[faculty_list['ICD10']==icd].tolist()
#     	if len(indexes) > 0:
#             for i in indexes:
#                 result.append(faculty_list.iloc[i]['Faculty_code'])
#     return result

# def get_falcuty_from_group(group):
#     faculty_group = pd.read_csv('./data/dictionary/faculty_group.csv')
#     result = []
#     indexes = faculty_group.index[faculty_group['group_onto']==group]
#     if len(indexes) > 0:
#         for i in indexes:
#             result.append(faculty_group.iloc[i]['faculty_code'])
#     return result

# if __name__ == "__main__":
#     icd = pd.read_csv("./gi.csv")
#     empty_list = 0
#     for i in range(icd.shape[0]):
#         a = get_faculty(icd.iloc[i]['icd']) + get_falcuty_from_group(icd.iloc[i]['g_label'])
#         if len(a) == 0:
#             empty_list += 1
#             print(icd.iloc[i]['icd'])
#     print(empty_list/icd.shape[0])
#     # print(get_faculty("C22.0"))