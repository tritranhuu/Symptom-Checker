
# file options
ONTOLOGY = "./data/data.owl"
ONTO2VEC = "./embedding/onto2vec.bin"

SIMILARITY_PRETRAINED = "./data/sim_pretrained.pkl"
DISEASES = "./data/diseases.pkl"
SYMPTOMS = "./data/symptoms.pkl"

LOGGING_PATH = "./user_history/data/"


# const options
SYMPTOM_PROGRESS = {
                    "Kéo dài và không dứt" : 2, "Lasting for long time" : 2,   
                    "Lúc bị lúc không" : 1, "Sometimes have somtimes not" : 1,
                    "Ngày càng nặng thêm" : 3, "More and more severe" : 3,
                    "Ngày càng giảm nhẹ dần" : -3, "More and more mild" : -3

                    }

SYMPTOM_TIME = {
                "Cách đây vài giờ" : 1, "For few hours" : 1,   
                "Cách đây vài ngày" : 2, "For few days" : 2,
                "Đã xuất hiện từ vài tháng" : 3, "For few months" : 3,
                "Đã xuất hiện nhiều năm" : 4, "For few years" : 4
                }

SYMPTOM_LEVEL = range(1,5)

