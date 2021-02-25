from deepcare.inference.inference import DC_SymptomChecker

class RedisSymptomChecker():
    def __init__(self):
        self.user = None
        self.symptom_init = None
        self.question_answer = None
        self.diseases_init = None
        self.symptoms_init = None
        self.related_symptoms = None
        self.answer_tracking = None
        self.disease_tracking = None
        self.same_disease_count = None
        self.prev_answer = None
        self.positive_user_symptoms = None
        self.negative_user_symptoms = None
        self.positive_user_causes = None
        self.negative_user_causes = None
        self.diseases_score = None
        self.symptoms_to_ask = None


    def set_from_symptom_checker(self, symptom_checker):
        self.user = symptom_checker.user
        self.symptom_init = symptom_checker.symptom_init
        self.question_answer = symptom_checker.question_answer
        self.diseases_init = symptom_checker.diseases_init
        self.symptoms_init = symptom_checker.symptoms_init
        self.related_symptoms = symptom_checker.related_symptoms
        self.answer_tracking = symptom_checker.answer_tracking
        self.disease_tracking = symptom_checker.disease_tracking
        self.same_disease_count = symptom_checker.same_disease_count
        self.prev_answer = symptom_checker.prev_answer
        self.positive_user_symptoms = symptom_checker.positive_user_symptoms
        self.negative_user_symptoms = symptom_checker.negative_user_symptoms
        self.positive_user_causes = symptom_checker.positive_user_causes
        self.negative_user_causes = symptom_checker.negative_user_causes
        self.diseases_score = symptom_checker.diseases_score
        self.symptoms_to_ask = symptom_checker.symptoms_to_ask


    def load_to_symptom_checker(self, inference, query):
        symptom_checker = DC_SymptomChecker(self.user, self.symptom_init, inference, query)
        symptom_checker.question_answer = self.question_answer
        symptom_checker.diseases_init = self.diseases_init
        symptom_checker.symptoms_init = self.symptoms_init
        symptom_checker.related_symptoms = self.related_symptoms
        symptom_checker.answer_tracking = self.answer_tracking
        symptom_checker.disease_tracking = self.disease_tracking
        symptom_checker.same_disease_count = self.same_disease_count
        symptom_checker.prev_answer = self.prev_answer
        symptom_checker.positive_user_symptoms = self.positive_user_symptoms
        symptom_checker.negative_user_symptoms = self.negative_user_symptoms
        symptom_checker.positive_user_causes = self.positive_user_causes
        symptom_checker.negative_user_causes = self.negative_user_causes
        symptom_checker.diseases_score = self.diseases_score 
        symptom_checker.symptoms_to_ask = self.symptoms_to_ask
        return symptom_checker