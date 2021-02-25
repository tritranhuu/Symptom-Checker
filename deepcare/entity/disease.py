# from setting import setting
# from deepcare.database.query import DC_Query
# from deepcare.entity.symptom import Symptom

class Disease():
    def __init__(self, label=None, iri=None):
        self.label = label
        self.iri = iri
        
        self.symptoms = None
        self.main_symptoms = None
        self.probably_symptoms = None

        self.serious_symptoms = None

        self.age = None
        self.gender_common = None
        self.gender_only = None
        self.causes = None
        self.label_en = None

        self.vector = None

    def set_symptoms(self, symptoms):
        self.symptoms = symptoms

    def set_main_symptoms(self, main_symptoms):
        self.main_symptoms = main_symptoms

    def set_probably_symptoms(self, probably_symptoms):
        self.probably_symptoms = probably_symptoms

    def set_serious_symptoms(self, serious_symptoms):
        self.serious_symptoms = serious_symptoms

    def set_age(self, age):
        self.age = age

    def set_gender_common(self, gender_common):
        self.gender_common = gender_common

    def set_gender_only(self, gender_only):
        self.gender_only = gender_only

    def set_causes(self, causes):
        self.causes = causes
    
    def set_label_en(self, label_en):
        self.label_en = label_en