import hashlib
import uuid
import json
import setting

class SymptomCheckerLogging():
    def __init__(self, data):
        suffix = uuid.uuid4().hex
        self.id = str(hashlib.sha1((data.user.name + str(data.user.age_num) + data.user.gender).encode('utf-8') + suffix.encode('utf-8')).hexdigest())

        self.user = {
                    "name" : data.user.name,
                    "age" : data.user.age_num,
                    "gender" : data.user.gender,
                    "symptom_checker" : {
                        "symptom_init" : data.inference.symptoms[data.symptom_init].label,
                        "question_answer" : data.question_answer,
                        "pos_causes" : data.positive_user_causes,
                        "neg_causes" : data.negative_user_causes,
                        "pos_symptoms" : [data.inference.symptoms[s].label for s in data.positive_user_symptoms],
                        "neg_symptoms" : [data.inference.symptoms[s].label for s in data.negative_user_symptoms],
                        "top_diseaes" : [(data.inference.diseases[k].label, v) for k, v in data.diseases_score.items()]
                    }}
    def save(self):
        file_name = setting.LOGGING_PATH + self.id +".json" 
        with open(file_name, 'w', encoding='utf8') as fp:
            json.dump(self.user, fp, indent=4, ensure_ascii=False)

